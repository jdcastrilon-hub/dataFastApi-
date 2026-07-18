from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_medio , schema_medio
from app.modules.comercial.mediopago import model_medio

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:] if logs else logs

# Obtener todas las bodegas ordenadas de mayor a menor
def get_medios_pago(db: Session):
    return db.query(model_medio.MedioPago).order_by(model_medio.MedioPago.orden).all()

#Paginacion (filtrada por empresa, a diferencia del combo de arriba que es global)
def get_medios_pago_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_medio.MedioPago).filter(model_medio.MedioPago.id_emp == idempresa)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(model_medio.MedioPago.tipo.ilike(patron))

    total_records = query.count()

    offset = page * size
    items = query\
        .order_by(desc(model_medio.MedioPago.fecha_mod))\
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

# Obtener un medio de pago por ID
def get_medio_pago_by_id(db: Session, id: int):
    return db.query(model_medio.MedioPago).filter(model_medio.MedioPago.id == id).first()

# Crear un medio de pago
def create_medio_pago(db: Session, obj: schema_medio.MedioPagoCreate):
    db_medio = model_medio.MedioPago(
        id_emp=obj.id_emp,
        tipo=obj.tipo,
        orden=obj.orden,
        logs=_limitar_logs([log.model_dump() for log in obj.logs] if obj.logs else []),
        fecha_mod=obj.fecha_mod
    )
    db.add(db_medio)
    db.commit()
    db.refresh(db_medio)
    return db_medio

# Actualizar un medio de pago
def update_medio_pago(db: Session, id: int, obj: schema_medio.MedioPagoCreate):
    db_medio = db.query(model_medio.MedioPago).filter(model_medio.MedioPago.id == id).first()
    if not db_medio:
        return None

    db_medio.tipo = obj.tipo
    db_medio.orden = obj.orden
    db_medio.logs = _limitar_logs([log.model_dump() for log in obj.logs] if obj.logs else [])
    db_medio.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(db_medio)
    return db_medio

# Eliminar un medio de pago
def delete_medio_pago(db: Session, id: int):
    db_medio = db.query(model_medio.MedioPago).filter(model_medio.MedioPago.id == id).first()
    if not db_medio:
        return None

    db.delete(db_medio)
    db.commit()
    return db_medio
