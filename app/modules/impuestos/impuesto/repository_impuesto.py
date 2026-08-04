from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import modal_impuesto

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

# Lista simple (usada por el formulario de articulos y por los combos de
# compra-directa/venta-directa/venta-pos), filtrada por empresa.
def get_impuestos(db: Session, id_emp: int):
    return db.query(modal_impuesto.Impuesto)\
        .filter(modal_impuesto.Impuesto.id_emp == id_emp)\
        .all()

# Obtener un impuesto por ID
def get_impuesto(db: Session, id_impuesto: int):
    return db.query(modal_impuesto.Impuesto)\
        .options(joinedload(modal_impuesto.Impuesto.tipo_impuesto))\
        .filter(modal_impuesto.Impuesto.id == id_impuesto).first()

# Crear un impuesto
def create_impuesto(db: Session, obj):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    db_impuesto = modal_impuesto.Impuesto(**data)

    db.add(db_impuesto)
    db.commit()
    db.refresh(db_impuesto)
    return db_impuesto

# Actualizar impuesto
def update_impuesto(db: Session, id_impuesto: int, obj):
    db_query = db.query(modal_impuesto.Impuesto).filter(modal_impuesto.Impuesto.id == id_impuesto)
    db_impuesto = db_query.first()

    if db_impuesto:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_impuesto)
    return db_impuesto

# Eliminar impuesto
def delete_impuesto(db: Session, id_impuesto: int):
    db_impuesto = db.query(modal_impuesto.Impuesto).filter(modal_impuesto.Impuesto.id == id_impuesto).first()
    if db_impuesto:
        db.delete(db_impuesto)
        db.commit()
    return db_impuesto

# Paginacion (filtrada por empresa)
def get_impuestos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(modal_impuesto.Impuesto)\
        .filter(modal_impuesto.Impuesto.id_emp == id_emp)

    # Filtro de busqueda por tasa o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                modal_impuesto.Impuesto.tasa_impu.ilike(patron),
                modal_impuesto.Impuesto.nombre_tasa.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(joinedload(modal_impuesto.Impuesto.tipo_impuesto))\
        .order_by(desc(modal_impuesto.Impuesto.fecha_mod))\
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

# Catalogo de tipos de impuesto (global, sin CRUD propio, solo lectura)
def get_tipos_impuesto(db: Session):
    return db.query(modal_impuesto.TipoImpuesto)\
        .order_by(modal_impuesto.TipoImpuesto.nombre_impuesto)\
        .all()
