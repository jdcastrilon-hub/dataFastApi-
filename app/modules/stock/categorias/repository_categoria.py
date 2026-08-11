from fastapi import HTTPException
from sqlalchemy import desc, or_, text
from sqlalchemy.orm import Session , joinedload
from . import models, schema_categoria
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_categoria
CODIGO_NUMERADOR_CATEGORIA = "CATEGORIA"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_cod_categoria(db: Session, id_emp: int, cod_categoria_manual):
    """
    Asigna el codCategoria desde el numerador de la empresa (2 digitos, ver
    docs/tecnica/specs/core/autonumeracion-catalogos.md). Si la empresa tiene
    "requiere_consecutivo" en False, respeta lo que haya enviado el formulario
    (modo manual) - mismo criterio que _obtener_cod_articulo/_obtener_cod_bodega.
    """
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_CATEGORIA)
    if siguiente is None:
        return cod_categoria_manual

    return repository_numerador.formatear_numerador(siguiente, longitud=2)


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
    logs_dict = _limitar_logs([log.model_dump() for log in cat.logs])
    # 1. Crear el objeto principal
    db_categoria = models.Categoria(
        id_emp=cat.id_emp,
        cod_categoria=_obtener_cod_categoria(db, cat.id_emp, cat.cod_categoria),
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
    # 1. Buscar la categoria existente
    bd_categoria = db.query(models.Categoria).filter(models.Categoria.id == id_categoria).first()
    if not bd_categoria:
        raise HTTPException(status_code=404, detail="Categroia no encontrado")

    try:
         # Seteamos los valores nuevos sobre el objeto recuperado
        bd_categoria.cod_categoria = obj.cod_categoria
        bd_categoria.nom_categoria = obj.nom_categoria
        bd_categoria.estado = obj.estado


        bd_categoria.logs = _limitar_logs([log.model_dump() for log in obj.logs])
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

    except HTTPException:
        raise
    except Exception:
        # Se conserva el rollback (varios pasos antes del commit final), pero se
        # relanza la excepción original en vez de envolverla en un mensaje crudo: así
        # el manejador global (IntegrityError/DataError) responde con un mensaje amigable.
        db.rollback()
        raise

def delete_categoria(db: Session, id_categoria: int):
    # 1. Buscamos la categoria para confirmar que existe
    bd_categoria = db.query(models.Categoria).filter(
        models.Categoria.id == id_categoria
    ).first()

    if not bd_categoria:
        # Si no existe, no hay nada que borrar
        return None

    try:
        # 2. Borramos los hijos primero
        db.query(models.Subcategoria).filter(
            models.Subcategoria.categoria_id == id_categoria
        ).delete()

        db.query(models.SubcategoriaModel).filter(
            models.SubcategoriaModel.categoria_id == id_categoria
        ).delete()

        # 3. Borramos el padre
        db.delete(bd_categoria)

        # 4. Guardamos cambios
        db.commit()

        return bd_categoria

    except Exception:
        # Se conserva el rollback (borrado en varios pasos), pero se relanza la
        # excepción original para que el manejador global de IntegrityError la
        # convierta en el mensaje de "registro en uso en otro módulo".
        db.rollback()
        raise

#Paginacion
def get_categorias_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(models.Categoria).filter(models.Categoria.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                models.Categoria.cod_categoria.ilike(patron),
                models.Categoria.nom_categoria.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(models.Categoria.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    } 
