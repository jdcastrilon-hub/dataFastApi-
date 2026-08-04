from sqlalchemy import desc, or_
from sqlalchemy.orm import Session , joinedload
from . import model_unidad

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
# Se aplica aquí (y no solo en el frontend) para que quede garantizado sin
# importar quién envíe el request.
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

# Obtener todas las unidades de la empresa
def get_unidades(db: Session, id_emp: int):
    return db.query(model_unidad.Unidad)\
        .filter(model_unidad.Unidad.id_emp == id_emp)\
        .all()

# Obtener una unidad por ID
def get_unidad(db: Session, unidad_id: int):
    return db.query(model_unidad.Unidad).filter(model_unidad.Unidad.id == unidad_id).first()

# Crear una unidad
def create_unidad(db: Session, obj):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    db_unidad = model_unidad.Unidad(**data)

    db.add(db_unidad)
    db.commit()
    db.refresh(db_unidad) # Aquí se recupera el ID generado por el autonumérico
    return db_unidad

# Actualizar unidad
def update_unidad(db: Session, unidad_id: int, obj):
    db_query = db.query(model_unidad.Unidad).filter(model_unidad.Unidad.id == unidad_id)
    db_unidad = db_query.first()

    if db_unidad:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_unidad)
    return db_unidad

# Eliminar unidad
def delete_unidad(db: Session, unidad_id: int):
    db_unidad = db.query(model_unidad.Unidad).filter(model_unidad.Unidad.id == unidad_id).first()
    if db_unidad:
        db.delete(db_unidad)
        db.commit()
    return db_unidad

#Paginacion
def get_unidades_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_unidad.Unidad)\
        .filter(model_unidad.Unidad.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_unidad.Unidad.cod_unidad.ilike(patron),
                model_unidad.Unidad.nom_unidad.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_unidad.Unidad.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
