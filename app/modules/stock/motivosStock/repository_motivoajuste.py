from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_motivoajuste ,schema_ajuste

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def get_all(db: Session, id_emp: int):
        return db.query(model_motivoajuste.MotivoAjuste)\
            .filter(model_motivoajuste.MotivoAjuste.id_emp == id_emp)\
            .all()

# Obtener un motivo por ID
def get_motivo(db: Session, id_motivo: int):
    return db.query(model_motivoajuste.MotivoAjuste).filter(model_motivoajuste.MotivoAjuste.id == id_motivo).first()

# Crear un motivo
def create_motivo(db: Session, obj: schema_ajuste.MotivoAjusteCreate):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    db_motivo = model_motivoajuste.MotivoAjuste(**data)

    db.add(db_motivo)
    db.commit()
    db.refresh(db_motivo) # Aquí se recupera el ID generado por el autonumérico
    return db_motivo

# Actualizar motivo
def update_motivo(db: Session, id_motivo: int, obj: schema_ajuste.MotivoAjusteCreate):
    db_query = db.query(model_motivoajuste.MotivoAjuste).filter(model_motivoajuste.MotivoAjuste.id == id_motivo)
    db_motivo = db_query.first()

    if db_motivo:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_motivo)
    return db_motivo

# Eliminar motivo
def delete_motivo(db: Session, id_motivo: int):
    db_motivo = db.query(model_motivoajuste.MotivoAjuste).filter(model_motivoajuste.MotivoAjuste.id == id_motivo).first()
    if db_motivo:
        db.delete(db_motivo)
        db.commit()
    return db_motivo

#Paginacion
def get_motivos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_motivoajuste.MotivoAjuste)\
        .filter(model_motivoajuste.MotivoAjuste.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_motivoajuste.MotivoAjuste.cod_motivo.ilike(patron),
                model_motivoajuste.MotivoAjuste.nom_motivo.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_motivoajuste.MotivoAjuste.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
