from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import models, schema_categoria


def get_categorias(db: Session, skip: int = 0, limit: int = 100):
    # .options(joinedload(...)) se puede usar para optimizar, 
    # pero al tener relationship configurado, SQLAlchemy lo manejará.
    return db.query(models.Categoria).offset(skip).limit(limit).all()

# Obtener una bodega por ID
def get_categoriaByID(db: Session, categoria_id: int):
    return db.query(models.Categoria)\
        .options(joinedload(models.Categoria.subcategorias))\
        .filter(models.Categoria.id == categoria_id)\
        .first()

def create_categoria(db: Session, cat: schema_categoria.CategoriaCreate):

    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = [log.model_dump() for log in cat.logs]
    # 1. Crear el objeto principal
    db_categoria = models.Categoria(
        id_emp=cat.id_emp,
        cod_categoria=cat.cod_categoria,
        nom_categoria=cat.nom_categoria,
        estado=cat.estado,
        logs=logs_dict,
        fecha_mod=cat.fecha_mod
    )
    db.add(db_categoria)
    db.flush() # Para obtener el ID de la categoria antes de insertar subcategorías

    # 2. Crear las subcategorías vinculadas
    for sub in cat.subcategorias:
        db_sub = models.Subcategoria(
            categoria_id=db_categoria.id,
            cod_subcategoria=sub.cod_subcategoria,
            nom_subcategoria=sub.nom_subcategoria
        )
        db.add(db_sub)

    db.commit()
    db.refresh(db_categoria)
    return db_categoria

#Paginacion
def get_bodegas_paginated(db: Session, page: int, size: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(models.Categoria).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = db.query(models.Categoria).order_by(desc(models.Categoria.fecha_mod)).offset(offset).limit(size).all()
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
