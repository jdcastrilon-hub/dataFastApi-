from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload
from . import model_conceptos, schema_conceptos

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:]


#Paginacion
def get_conceptos_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_conceptos.MConceptoCaja).filter(model_conceptos.MConceptoCaja.id_emp == idempresa)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(model_conceptos.MConceptoCaja.nom_concepto.ilike(patron))

    total_records = query.count()

    offset = page * size
    items = query\
        .order_by(desc(model_conceptos.MConceptoCaja.fecha_mod))\
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

# Conceptos activos asociados a un usuario, filtrados por signo (1=Ingreso/
# -1=Gasto) - usado por "Movimiento Caja" (comercial) para poblar el combo
# segun el tipo de movimiento elegido.
def get_conceptos_por_usuario(db: Session, id_usuario: int, idempresa: int, signo: int):
    return db.query(model_conceptos.MConceptoCaja)\
        .join(model_conceptos.MConceptoCajaXUser)\
        .filter(
            model_conceptos.MConceptoCajaXUser.id_usuario == id_usuario,
            model_conceptos.MConceptoCaja.id_emp == idempresa,
            model_conceptos.MConceptoCaja.signo == signo,
            model_conceptos.MConceptoCaja.status == True
        ).all()

# Obtener un concepto por ID
def get_concepto_by_id(db: Session, id: int):
    return db.query(model_conceptos.MConceptoCaja).filter(model_conceptos.MConceptoCaja.id == id).options(
        joinedload(model_conceptos.MConceptoCaja.usuarios).joinedload(model_conceptos.MConceptoCajaXUser.usuario)
    ).first()

# Actualizar concepto
def update_concepto(db: Session, id: int, obj: schema_conceptos.ConceptoCreate):
    try:
        db_concepto = db.query(model_conceptos.MConceptoCaja).filter(model_conceptos.MConceptoCaja.id == id).first()
        if not db_concepto:
            raise HTTPException(status_code=404, detail="Concepto no encontrado")

        db_concepto.nom_concepto = obj.nom_concepto
        db_concepto.signo = obj.signo
        db_concepto.status = obj.status
        db_concepto.aplica_limit = obj.aplica_limit
        db_concepto.imp_limit = obj.imp_limit if obj.aplica_limit else None
        db_concepto.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        db_concepto.fecha_mod = obj.fecha_mod

        # Reemplazar usuarios asignados (borrar e reinsertar, igual que en cajas)
        db.query(model_conceptos.MConceptoCajaXUser).filter(model_conceptos.MConceptoCajaXUser.id_concepto == id).delete()
        db.flush()
        for usuario in obj.usuarios:
            db.add(model_conceptos.MConceptoCajaXUser(id_concepto=id, id_usuario=usuario.id_usuario))

        db.commit()
        db.refresh(db_concepto)
        return db_concepto

    except HTTPException:
        raise
    except (IntegrityError, DataError):
        db.rollback()
        raise

# Eliminar un concepto (dato maestro simple)
def delete_concepto(db: Session, id: int):
    db_concepto = db.query(model_conceptos.MConceptoCaja).filter(model_conceptos.MConceptoCaja.id == id).first()
    if not db_concepto:
        return None

    db.delete(db_concepto)  # cascade borra m_conceptoscajaxuser
    db.commit()
    return db_concepto


def create_concepto(db: Session, obj: schema_conceptos.ConceptoCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

    db_concepto = model_conceptos.MConceptoCaja(
        id_emp=obj.id_emp,
        nom_concepto=obj.nom_concepto,
        signo=obj.signo,
        status=obj.status,
        aplica_limit=obj.aplica_limit,
        imp_limit=obj.imp_limit if obj.aplica_limit else None,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_concepto)
    db.flush()

    for usuario in obj.usuarios:
        db.add(model_conceptos.MConceptoCajaXUser(id_concepto=db_concepto.id, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_concepto)
    return db_concepto
