from fastapi import HTTPException
from sqlalchemy import desc, or_, text
from sqlalchemy.orm import Session , joinedload
from . import models, schema_categoria
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_categoria
CODIGO_NUMERADOR_CATEGORIA = "CATEGORIA"

# Prefijo del numerador de subcategorias - NO es un codigo fijo: cada categoria
# tiene su propio numerador independiente, con clave "SUBCATEGORIA_<id_categoria>"
# (decision explicita 2026-08-07: la numeracion de subcategoria reinicia en 01
# por cada categoria, no es un contador corrido para toda la empresa).
CODIGO_NUMERADOR_SUBCATEGORIA = "SUBCATEGORIA"

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

def _obtener_cod_subcategoria(db: Session, id_emp: int, categoria_id: int, cod_subcategoria_manual):
    """
    Asigna el codSubCategoria desde un numerador PROPIO de esa categoria (no
    uno solo por empresa) - la clave real en md_numeradores es dinamica,
    "SUBCATEGORIA_<categoria_id>", asi que cada categoria arranca su propia
    serie 01,02,03... independiente de las demas. Solo se llama para
    subcategorias nuevas; una ya existente nunca se renumera.
    """
    codigo_numerador = f"{CODIGO_NUMERADOR_SUBCATEGORIA}_{categoria_id}"
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, codigo_numerador)
    if siguiente is None:
        return cod_subcategoria_manual

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

    # 2. Crear las subcategorías vinculadas (todas son nuevas: la categoria
    # recien se creo, asi que db_categoria.id ya existe gracias al flush de arriba)
    for sub in cat.subcategorias:
        db_sub = models.Subcategoria(
            categoria_id=db_categoria.id,
            cod_subcategoria=_obtener_cod_subcategoria(db, cat.id_emp, db_categoria.id, sub.cod_subcategoria),
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
            # Solo las filas nuevas (id=0, ver sp_categorias_updatesubcategorias)
            # piden numerador - una subcategoria ya existente nunca se renumera.
            es_nueva = not codigos.id
            cod_subcategoria = (
                _obtener_cod_subcategoria(db, bd_categoria.id_emp, id_categoria, codigos.cod_subcategoria)
                if es_nueva else codigos.cod_subcategoria
            )
            db_codigos = models.SubcategoriaModel(
                categoria_id=id_categoria,
                id=codigos.id or 0,
                linea=i, #Numerador de linea
                cod_subcategoria=cod_subcategoria,
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

# Combo de categorias activas de la empresa (usado por selects de otros
# formularios, ej. Utilidad x Categoria).
def get_categorias_combo(db: Session, id_emp: int):
    return db.query(models.Categoria)\
        .filter(models.Categoria.id_emp == id_emp, models.Categoria.estado == True)\
        .order_by(models.Categoria.nom_categoria)\
        .all()

# Combo de subcategorias de UNA categoria puntual (cascada del combo anterior).
# Se filtra tambien por id_emp via join a Categoria, aunque Subcategoria no
# tenga la columna propia - mismo criterio que otras entidades sin id_emp
# directo (ver m_bodegas).
def get_subcategorias_combo(db: Session, id_categoria: int, id_emp: int):
    return db.query(models.Subcategoria)\
        .join(models.Categoria, models.Categoria.id == models.Subcategoria.categoria_id)\
        .filter(models.Subcategoria.categoria_id == id_categoria, models.Categoria.id_emp == id_emp)\
        .order_by(models.Subcategoria.nom_subcategoria)\
        .all()

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
