from sqlalchemy import desc, or_, text
from sqlalchemy.orm import Session
from . import model_bodega, schema_bodega

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
# Se aplica aquí (y no solo en el frontend) para que quede garantizado sin
# importar quién envíe el request.
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

# Obtener todas las bodegas ordenadas de mayor a menor
def get_bodegas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model_bodega.Bodega).order_by(desc(model_bodega.Bodega.fecha_mod)).offset(skip).limit(limit).all()

# Obtener todas las bodegas
def get_bodegas_combo(db: Session):
    return db.query(model_bodega.Bodega).all()

# Obtener una bodega por ID
def get_bodega(db: Session, bodega_id: int):
    return db.query(model_bodega.Bodega).filter(model_bodega.Bodega.id == bodega_id).first()

# Crear una bodega
def create_bodega(db: Session, bodega: schema_bodega.BodegaCreate):
    # Convertimos el schema a un diccionario y lo pasamos al modelo
    data = bodega.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    db_bodega = model_bodega.Bodega(**data)

    db.add(db_bodega)
    db.commit()
    db.refresh(db_bodega) # Aquí se recupera el ID generado por el autonumérico
    return db_bodega

# Actualizar bodega
def update_bodega(db: Session, bodega_id: int, bodega_data: schema_bodega.BodegaCreate):
    db_query = db.query(model_bodega.Bodega).filter(model_bodega.Bodega.id == bodega_id)
    db_bodega = db_query.first()

    if db_bodega:
        # Actualizamos los campos dinámicamente
        update_data = bodega_data.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_bodega)
    return db_bodega

# Eliminar bodega
def delete_bodega(db: Session, bodega_id: int):
    db_bodega = db.query(model_bodega.Bodega).filter(model_bodega.Bodega.id == bodega_id).first()
    if db_bodega:
        db.delete(db_bodega)
        db.commit()
    return db_bodega

#Paginacion
def get_bodegas_paginated(db: Session, page: int, size: int, texto: str = None):
    query = db.query(model_bodega.Bodega)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_bodega.Bodega.cod_bodega.ilike(patron),
                model_bodega.Bodega.nom_bodega.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_bodega.Bodega.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

def get_stock_disponible(db: Session, idArticulo: int,idCodbarra: int, idBodega: int, idEstado: int):
    # Definimos el query nativo llamando a la función
    query = text("""
            SELECT 
                s.stock AS "stock"
            FROM stockdisponiblexBodega(:param_articulo_id,:param_id_codbarra, :param_bodega_id, :param_estado_id) AS s
    """)
        
    # Ejecutamos con los parámetros
    result = db.execute(query, {
            "param_articulo_id": idArticulo,
            "param_id_codbarra": idCodbarra,
            "param_bodega_id": idBodega,
            "param_estado_id": idEstado
    })
        
    # Convertimos los resultados a diccionarios para que Pydantic los valide
    return result.mappings().all()