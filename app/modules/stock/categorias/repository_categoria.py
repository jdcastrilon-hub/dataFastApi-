from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import models, schema_categoria


def get_categorias(db: Session, skip: int = 0, limit: int = 100):
    # .options(joinedload(...)) se puede usar para optimizar, 
    # pero al tener relationship configurado, SQLAlchemy lo manejará.
    return db.query(models.Categoria).offset(skip).limit(limit).all()

# Obtener una bodega por ID
def get_categoriaByID(db: Session, categoria_id: int):
    return db.query(models.Categoria)\
        .options(
            joinedload(models.Categoria.subcategorias)
            .joinedload(models.Subcategoria.articulos) # Cargamos los artículos también para validar si tiene relacion
        )\
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

# Actualizar Categoria
def update_categoria(db: Session, id_categoria: int, obj : schema_categoria.CategoriaCreate):
    try:
        # 1. Buscar la categoria existente
        bd_categoria = db.query(models.Categoria).filter(models.Categoria.id == id_categoria).first()
        if not bd_categoria:
            raise HTTPException(status_code=404, detail="Categroia no encontrado")
        
         # Seteamos los valores nuevos sobre el objeto recuperado
        bd_categoria.cod_categoria = obj.cod_categoria
        bd_categoria.nom_categoria = obj.nom_categoria
        bd_categoria.estado = obj.estado
       
    
        bd_categoria.logs = [log.model_dump() for log in obj.logs]
        bd_categoria.fecha_mod = obj.fecha_mod

         # 2. Crear las subcategorias model
        db.query(models.SubcategoriaModel).filter(models.SubcategoriaModel.categoria_id == id_categoria).delete()        
        db.flush()
         
        for i,codigos in enumerate(obj.subcategorias, start=1):
            db_codigos = models.SubcategoriaModel(
                categoria_id=id_categoria,
                id=codigos.id or 0,
                linea=i, #Numerador de linea
                cod_subcategoria=codigos.cod_subcategoria,
                nom_subcategoria=codigos.nom_subcategoria,                
            )
            db.add(db_codigos)
        db.flush()
        
        db.execute(
                text("CALL public.sp_categorias_updatesubcategorias(:p_id_categoria)"), 
                {"p_id_categoria": id_categoria}
            )   
            

        db.commit()
        db.refresh(bd_categoria)
        return bd_categoria
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al editar la categoria: {str(e)}")  
    
def delete_categoria(db: Session, id_categoria: int):
        # 1. Borramos los hijos primero
        db.query(models.Subcategoria).filter(
            models.Subcategoria.categoria_id == id_categoria
        ).delete()

        db.query(models.SubcategoriaModel).filter(
            models.SubcategoriaModel.categoria_id == id_categoria
        ).delete()
        
        # 2. Buscamos el artículo para confirmar que existe y retornarlo
        bd_categoria = db.query(models.Categoria).filter(
            models.Categoria.id == id_categoria
        ).first()

        if not bd_categoria:
            # Si no existe, no hay nada que borrar
            return None 

        # 3. Borramos el padre
        db.delete(bd_categoria)
        
        # 4. Guardamos cambios
        db.commit()
        
        return bd_categoria    

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
