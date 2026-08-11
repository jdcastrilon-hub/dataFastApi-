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


# Combo de listas base (nunca de cliente) para usar como selector en otros
# formularios (ej. venta-directa) - no tiene sentido ofrecer ahi una lista
# negociada de un cliente puntual, esa se resuelve por otro camino.
def get_listaprecio_combo(db: Session, id_emp: int, id_usuario: int):
    # La general nunca valida permiso (acceso implicito para todos); una lista
    # base no-general (ej. Mayorista) solo aparece si el usuario tiene una fila
    # en m_listaprecioxuser para ella. Las de cliente nunca entran aca (filtro
    # id_cliente IS NULL) - se tratan distinto (ver project_data_lista_precios_design).
    return db.query(model_listaprecio.MListaPrecio)\
        .filter(
            model_listaprecio.MListaPrecio.id_emp == id_emp,
            model_listaprecio.MListaPrecio.id_cliente.is_(None),
            model_listaprecio.MListaPrecio.activo.is_(True),
            or_(
                model_listaprecio.MListaPrecio.es_general.is_(True),
                model_listaprecio.MListaPrecio.usuarios.any(model_listaprecio.MListaPrecioXUser.id_usuario == id_usuario)
            )
        )\
        .order_by(model_listaprecio.MListaPrecio.nombre)\
        .all()


# A diferencia de get_listaprecio_combo, incluye tambien las listas de cliente:
# la carga masiva de precios puede apuntar a cualquier lista activa (ver diseño
# en project_data_lista_precios_design).
def get_listaprecio_combo_todas(db: Session, id_emp: int):
    return db.query(model_listaprecio.MListaPrecio)\
        .options(joinedload(model_listaprecio.MListaPrecio.cliente))\
        .filter(
            model_listaprecio.MListaPrecio.id_emp == id_emp,
            model_listaprecio.MListaPrecio.activo.is_(True)
        )\
        .order_by(model_listaprecio.MListaPrecio.nombre)\
        .all()


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
