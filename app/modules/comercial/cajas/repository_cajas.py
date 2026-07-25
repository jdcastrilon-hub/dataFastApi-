from fastapi import HTTPException
from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session , joinedload
from . import model_cajas, schema_cajas

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:]


#Paginacion
def get_cajas_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_cajas.MCaja).filter(model_cajas.MCaja.id_emp == idempresa)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_cajas.MCaja.cod_caja.ilike(patron),
                model_cajas.MCaja.nom_caja.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(joinedload(model_cajas.MCaja.sucursal))\
        .order_by(desc(model_cajas.MCaja.fecha_mod))\
        .offset(offset)\
        .limit(size)\
        .all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Cajas asociadas a un usuario (m_cajasxuser) - para venta-directa cuando el
# usuario no tiene un turno/caja POS abierto (escenario "administrador").
# Solo cajas NO POS: si el usuario tuviera una caja POS realmente activa, ya
# habria un turno abierto y el formulario habria tomado el Escenario A (turno)
# en vez de este picker manual - una caja POS nunca debe elegirse aca.
def get_cajas_por_usuario(db: Session, id_usuario: int, idempresa: int):
    return db.query(model_cajas.MCaja)\
        .join(model_cajas.MCajasXUser, model_cajas.MCajasXUser.id_caja == model_cajas.MCaja.id)\
        .filter(
            model_cajas.MCajasXUser.id_usuario == id_usuario,
            model_cajas.MCaja.id_emp == idempresa,
            model_cajas.MCaja.cajapos == False
        )\
        .order_by(model_cajas.MCaja.nom_caja)\
        .all()

# Obtener una caja por ID
def get_caja_by_id(db: Session, id: int):
    return db.query(model_cajas.MCaja).filter(model_cajas.MCaja.id == id).options(
        joinedload(model_cajas.MCaja.sucursal),
        joinedload(model_cajas.MCaja.cliente),
        joinedload(model_cajas.MCaja.usuarios).joinedload(model_cajas.MCajasXUser.usuario)
    ).first()

# Actualizar caja
def update_caja(db: Session, id: int, obj: schema_cajas.CajaCreate):
    try:
        db_caja = db.query(model_cajas.MCaja).filter(model_cajas.MCaja.id == id).first()
        if not db_caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        db_caja.id_sucursal_emp = obj.id_sucursal_emp
        db_caja.cod_caja = obj.cod_caja
        db_caja.nom_caja = obj.nom_caja
        db_caja.cajapos = obj.cajapos
        db_caja.horas_turno = obj.horas_turno
        db_caja.status = obj.status
        db_caja.id_cliente = obj.id_cliente
        db_caja.id_bodega = obj.id_bodega
        db_caja.id_estado = obj.id_estado
        db_caja.documento = obj.documento
        db_caja.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        db_caja.fecha_mod = obj.fecha_mod

        # Reemplazar usuarios asignados (borrar e reinsertar, igual que el detalle de un documento)
        db.query(model_cajas.MCajasXUser).filter(model_cajas.MCajasXUser.id_caja == id).delete()
        db.flush()
        for usuario in obj.usuarios:
            db.add(model_cajas.MCajasXUser(id_caja=id, id_usuario=usuario.id_usuario))

        db.commit()
        db.refresh(db_caja)
        return db_caja

    except HTTPException:
        raise
    except (IntegrityError, DataError):
        db.rollback()
        raise

# Eliminar una caja (no tiene impacto en stock/costos, es dato maestro simple).
# Si tiene turnos asociados, la FK de t_abrirturno rechaza el delete y el
# manejador global de IntegrityError ya devuelve un mensaje amigable.
def delete_caja(db: Session, id: int):
    db_caja = db.query(model_cajas.MCaja).filter(model_cajas.MCaja.id == id).first()
    if not db_caja:
        return None

    db.delete(db_caja)  # cascade borra m_cajasxuser
    db.commit()
    return db_caja


def create_caja(db: Session, obj: schema_cajas.CajaCreate):

    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
    # 1. Crear el objeto principal
    db_caja = model_cajas.MCaja(
        id_emp=obj.id_emp,
        id_sucursal_emp=obj.id_sucursal_emp,
        cod_caja=obj.cod_caja,
        nom_caja=obj.nom_caja,
        cajapos=obj.cajapos,
        horas_turno=obj.horas_turno,
        id_cliente=obj.id_cliente,
        id_bodega=obj.id_bodega,
        id_estado=obj.id_estado,
        documento=obj.documento,
        status=obj.status,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_caja)
    db.flush() # Envio a base de datos

    # 2. Crear las subcategorías vinculadas
    for usuarios in obj.usuarios:
        db_usuarios = model_cajas.MCajasXUser(
            id_caja=db_caja.id,
            id_usuario=usuarios.id_usuario
        )
        db.add(db_usuarios)

    db.commit()
    db.refresh(db_caja)
    return db_caja
