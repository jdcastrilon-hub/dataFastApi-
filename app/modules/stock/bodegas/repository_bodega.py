from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from . import model_bodega, schema_bodega

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
    db_bodega = model_bodega.Bodega(**bodega.model_dump())
    
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
def get_bodegas_paginated(db: Session, page: int, size: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(model_bodega.Bodega).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = db.query(model_bodega.Bodega).order_by(desc(model_bodega.Bodega.fecha_mod)).offset(offset).limit(size).all()
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

def get_stock_disponible(db: Session, id_articulo: int, id_bodega: int, id_estado: int):
        # Definimos el query nativo llamando a la función
        query = text("""
            SELECT 
                s.id AS "idArticulo", 
                s.codigo_articulo AS "codArticulo", 
                s.nombre_articulo AS "nomArticulo", 
                s.ubicacion AS "ubicacion", 
                s.lote AS "lote", 
                s.stock AS "stock"
            FROM stockdisponiblexBodega(:idArticulo, :idBodega, :idEstado) AS s
        """)
        
        # Ejecutamos con los parámetros
        result = db.execute(query, {
            "idArticulo": id_articulo,
            "idBodega": id_bodega,
            "idEstado": id_estado
        })
        
        # Convertimos los resultados a diccionarios para que Pydantic los valide
        return result.mappings().all()