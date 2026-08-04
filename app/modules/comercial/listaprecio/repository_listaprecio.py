from fastapi import HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_listaprecio, schema_listaprecio

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def get_listaprecio_by_id(db: Session, id_lista: int):
    return db.query(model_listaprecio.MListaPrecio)\
        .options(
            joinedload(model_listaprecio.MListaPrecio.cliente),
            joinedload(model_listaprecio.MListaPrecio.usuarios).joinedload(model_listaprecio.MListaPrecioXUser.usuario)
        )\
        .filter(model_listaprecio.MListaPrecio.id_lista == id_lista)\
        .first()


def create_listaprecio(db: Session, obj: schema_listaprecio.ListaPrecioCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
    db_lista = model_listaprecio.MListaPrecio(
        id_emp=obj.id_emp,
        nombre=obj.nombre,
        # Una lista general aplica a todos por definicion: no tiene sentido que
        # ademas quede negociada para un cliente puntual.
        id_cliente=obj.id_cliente if not obj.es_general else None,
        es_general=obj.es_general,
        activo=obj.activo,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_lista)
    db.flush()

    # Igual que General: si es general no se guardan asignaciones (irrelevantes,
    # aplica para todos los usuarios sin excepcion).
    if not obj.es_general:
        for usuario in obj.usuarios:
            db.add(model_listaprecio.MListaPrecioXUser(id_lista=db_lista.id_lista, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_lista)
    return db_lista


def update_listaprecio(db: Session, id_lista: int, obj: schema_listaprecio.ListaPrecioCreate):
    try:
        db_lista = db.query(model_listaprecio.MListaPrecio).filter(model_listaprecio.MListaPrecio.id_lista == id_lista).first()
        if not db_lista:
            raise HTTPException(status_code=404, detail="Lista de precios no encontrada")

        db_lista.nombre = obj.nombre
        db_lista.id_cliente = obj.id_cliente if not obj.es_general else None
        db_lista.es_general = obj.es_general
        db_lista.activo = obj.activo
        db_lista.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        db_lista.fecha_mod = obj.fecha_mod

        # Reemplazar usuarios asignados (borrar e reinsertar, igual que Cajas).
        db.query(model_listaprecio.MListaPrecioXUser).filter(model_listaprecio.MListaPrecioXUser.id_lista == id_lista).delete()
        db.flush()
        if not obj.es_general:
            for usuario in obj.usuarios:
                db.add(model_listaprecio.MListaPrecioXUser(id_lista=id_lista, id_usuario=usuario.id_usuario))

        db.commit()
        db.refresh(db_lista)
        return db_lista

    except HTTPException:
        raise
    except (Exception,):
        db.rollback()
        raise


# Eliminar (sin impacto en precios/ventas historicas todavia - m_reglaprecio y
# p_precios/s_precioxarticulo no existen aun en este modulo, ver design doc).
def delete_listaprecio(db: Session, id_lista: int):
    db_lista = db.query(model_listaprecio.MListaPrecio).filter(model_listaprecio.MListaPrecio.id_lista == id_lista).first()
    if not db_lista:
        return None

    db.delete(db_lista)  # cascade borra m_listaprecioxuser
    db.commit()
    return db_lista


def get_listaprecio_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_listaprecio.MListaPrecio)\
        .options(joinedload(model_listaprecio.MListaPrecio.cliente))\
        .filter(model_listaprecio.MListaPrecio.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(or_(model_listaprecio.MListaPrecio.nombre.ilike(patron)))

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_listaprecio.MListaPrecio.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
