from fastapi import HTTPException
from sqlalchemy import desc, exists, false, or_, text
from sqlalchemy.orm import Session , joinedload
from . import model_articulos , schema_articulos
from app.modules.stock.categorias import models
from app.modules.core.negocios import model_negocios
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_articulo
CODIGO_NUMERADOR_ARTICULO = "ARTICULO"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_negocio(db: Session, id_negocio: int):
    return db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id == id_negocio).first()

def _obtener_cod_articulo(db: Session, negocio, cod_articulo_manual):
    """
    Asigna el codArticulo desde el numerador de la empresa dueña del negocio.
    Si esa empresa tiene "requiere_consecutivo" en False, respeta lo que haya
    enviado el formulario (modo manual).
    """
    if not negocio:
        return cod_articulo_manual

    siguiente = repository_numerador.siguiente_numerador(db, negocio.id_emp, CODIGO_NUMERADOR_ARTICULO)
    if siguiente is None:
        return cod_articulo_manual

    return repository_numerador.formatear_numerador(siguiente)

# Obtener un articulo por ID
def get_articulo(db: Session, id_articulo: int):
    return db.query(model_articulos.Articulo).filter(model_articulos.Articulo.id_articulo == id_articulo).options(joinedload(model_articulos.Articulo.objnegocio)).first()

# Usado por Compra Directa (y cualquier grilla similar) para decidir si vale la
# pena mostrar la columna "Lote" - no existe un flag de "la empresa maneja
# lotes", se deriva de si al menos un articulo del catalogo lo maneja.
def existe_articulo_con_lote(db: Session, id_emp: int) -> bool:
    return db.query(model_articulos.Articulo.id_articulo)\
        .filter(model_articulos.Articulo.id_emp == id_emp, model_articulos.Articulo.maneja_lote == True)\
        .first() is not None

def find_codigoBarra_by_query(db: Session, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"

        return (
            db.query(
                model_articulos.CodigosBarra.id_articulo.label("idArticulo"),
                model_articulos.CodigosBarra.id_codbarra.label("idCodBarra"),
                model_articulos.CodigosBarra.cod_barra.label("codArticulo"),
                model_articulos.CodigosBarra.ref_barra.label("nomArticulo"),
                model_articulos.Articulo.maneja_lote.label("manejaLote")
            )
            .join(model_articulos.Articulo, model_articulos.Articulo.id_articulo == model_articulos.CodigosBarra.id_articulo)
            .filter(
                model_articulos.CodigosBarra.estado == True,
                or_(
                    model_articulos.CodigosBarra.cod_barra.ilike(search_filter),
                    model_articulos.CodigosBarra.ref_barra.ilike(search_filter)
                )
            )
            .order_by(model_articulos.CodigosBarra.ref_barra)
            .limit(20)
            .all()
        )

def find_articulos_by_query(db: Session, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"

        return (
            db.query(
                model_articulos.Articulo.id_articulo.label("idArticulo"),
                model_articulos.Articulo.cod_articulo.label("codArticulo"),
                model_articulos.Articulo.nom_articulo.label("nomArticulo"),
                model_articulos.Articulo.maneja_lote.label("manejaLote")
            )
            .filter(
                or_(
                    model_articulos.Articulo.cod_articulo.ilike(search_filter),
                    model_articulos.Articulo.nom_articulo.ilike(search_filter),
                    exists().where(
                        model_articulos.CodigosBarra.id_articulo == model_articulos.Articulo.id_articulo,
                        model_articulos.CodigosBarra.cod_barra.ilike(search_filter)
                    )
                )
            )
            .order_by(model_articulos.Articulo.nom_articulo)
            .limit(20)
            .all()
        )

def check_exists_cod_barra(db: Session, id_articulo: int, cod_barra: str) -> bool:
    # Esta consulta es muy eficiente porque no descarga datos, solo verifica existencia
    return db.query(
        exists().where(
            model_articulos.CodigosBarra.id_articulo == id_articulo,
            model_articulos.CodigosBarra.cod_barra == cod_barra
        )
    ).scalar()
        

#Paginacion
def generacion_codigobarra(db: Session, id_articulo: int, cod_barra: str):
    # 1. Validamos si el codigo de barra para el articulo seleccionado ya existe.
    existe = db.query(
        exists().where(
            model_articulos.CodigosBarra.id_articulo == id_articulo,
            model_articulos.CodigosBarra.cod_barra == cod_barra
        )
    ).scalar()

    idBarra=0

    if(existe==False):
        query = text("""
       SELECT nextval(:numerador) AS next_value
        """)  

        idBarra= db.execute(query, {"numerador": 'm_artxcodigobarra_id_codbarra_seq'}).mappings().first().get("next_value")
    
    return {
        "idArticulo":id_articulo,
        "idCodBarra": idBarra,
        "existe": existe
        
    }  

def consultar_stock_codigosbarra(db: Session, cadena: str, id_articulo: int):
    """
    Llama a la función fn_compras_masivo_stock_costo de PostgreSQL 
    para obtener saldos y costos de múltiples artículos en una sola petición.
    """
    try:
        # 1. Definimos la consulta a la función
        query = text("""
            SELECT idcodbarra, stock, movimientos 
            FROM public.articulo_obtener_stock_masivo(:articulo,:cadena)
        """)
        
        # 2. Ejecutamos pasando los parámetros
        result = db.execute(query, {
            "cadena": cadena, 
            "articulo": id_articulo
        })
        
        # 3. Mapeamos el resultado a una lista de diccionarios
        # Importante: Usamos nombres en CamelCase para que coincidan con tu Angular
        lista_actualizada = [
            {
                "idcodbarra": row.idcodbarra,
                "stock": row.stock,
                "movimientos": row.movimientos
            }
            for row in result
        ]
        
        return lista_actualizada    

    except Exception as e:
        # Log del error para depuración en Matrix
        print(f"Error en consultar_stock_lote: {str(e)}")
        return []


def get_lotes_articulo(db: Session, id_articulo: int, id_emp: int):
    result = db.execute(
        text("""
            SELECT L.id AS id_lote, L.codigo_lote, L.fec_vencimiento, COALESCE(S.cantidad, 0) AS cantidad
            FROM m_lotes L
            LEFT JOIN (
                SELECT id_lote, SUM(cantidad) AS cantidad
                FROM s_stkbodegaxlote
                WHERE id_articulo = :id_articulo AND id_emp = :id_emp
                GROUP BY id_lote
            ) S ON L.id = S.id_lote
            WHERE L.id_articulo = :id_articulo
            ORDER BY L.fec_vencimiento NULLS LAST
        """),
        {"id_articulo": id_articulo, "id_emp": id_emp}
    ).all()
    return [row._mapping for row in result]


def reservar_id_lote(db: Session, id_articulo: int, codigo_lote: str):
    """
    Mismo patron que generacion_codigobarra(): solo reserva un id real de la
    secuencia (nextval), sin insertar en m_lotes. El lote se materializa recien
    cuando se guarda la transaccion que lo usa (ver sp_stock_impacto_ajustestock),
    para que cancelar el formulario no deje lotes huerfanos.
    """
    existe = db.execute(
        text("SELECT 1 FROM m_lotes WHERE id_articulo = :id_articulo AND codigo_lote = :codigo_lote"),
        {"id_articulo": id_articulo, "codigo_lote": codigo_lote}
    ).first() is not None

    id_lote = 0
    if not existe:
        id_lote = db.execute(text("SELECT nextval('m_lotes_id_seq') AS next_value")).mappings().first().get("next_value")

    return {
        "idArticulo": id_articulo,
        "idLote": id_lote,
        "existe": existe
    }

#Paginacion
def get_articulos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_articulos.Articulo).filter(model_articulos.Articulo.id_emp == id_emp)

    # Filtro de busqueda por codigo, nombre o codigo de barra (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_articulos.Articulo.cod_articulo.ilike(patron),
                model_articulos.Articulo.nom_articulo.ilike(patron),
                exists().where(
                    model_articulos.CodigosBarra.id_articulo == model_articulos.Articulo.id_articulo,
                    model_articulos.CodigosBarra.cod_barra.ilike(patron)
                )
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = (
    query
    .options(
        joinedload(model_articulos.Articulo.objnegocio),
        joinedload(model_articulos.Articulo.subcategoria)
        .joinedload(models.Subcategoria.parent)
    )
    .order_by(desc(model_articulos.Articulo.fecha_mod))
    .offset(offset)
    .limit(size)
    .all()
)

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Crear un Articulo
def create_articulo(db: Session, obj: schema_articulos.ArticuloCreate):

     # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        # 1. Crear el objeto principal
        negocio = _obtener_negocio(db, obj.id_negocio)
        cod_articulo = _obtener_cod_articulo(db, negocio, obj.cod_articulo)
        bd_articulo = model_articulos.Articulo(
            cod_articulo = cod_articulo,
            nom_articulo = obj.nom_articulo,
            id_emp = negocio.id_emp if negocio else None,
            id_negocio = obj.id_negocio,
            id_categoria = obj.id_categoria,
            id_subcategoria = obj.id_subcategoria,
            id_unidad = obj.id_unidad,
            id_tiposervicio = obj.id_tiposervicio,
            id_impuesto = obj.id_impuesto,
            id_ref = obj.id_ref,
            activo_stock = obj.activo_stock,
            maneja_lote = obj.maneja_lote,
            stock_min = obj.stock_min,
            stock_max = obj.stock_max,
            grupo_contable = obj.grupo_contable,
            cta_inventario = obj.cta_inventario,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod)
        db.add(bd_articulo)
        db.flush() 

        # 2. Crear los codigos de barra
        for codigos in obj.codigosBarra:
            db_codigos = model_articulos.CodigosBarra(
                id_articulo=bd_articulo.id_articulo,
                cod_barra=codigos.cod_barra,
                ref_barra=codigos.ref_barra,
                estado= codigos.estado
            )
            db.add(db_codigos)

        db.commit()
        db.refresh(bd_articulo) 
        return bd_articulo

# Actualizar Compra
def update_articulo(db: Session, id_articulo: int, obj : schema_articulos.ArticuloCreate):
    # 1. Buscar la compra existente
    bd_articulo = db.query(model_articulos.Articulo).filter(model_articulos.Articulo.id_articulo == id_articulo).first()
    if not bd_articulo:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")

    try:
         # Seteamos los valores nuevos sobre el objeto recuperado
        bd_articulo.cod_articulo = obj.cod_articulo
        bd_articulo.nom_articulo = obj.nom_articulo
        bd_articulo.id_negocio = obj.id_negocio
        # id_emp se recalcula por si el negocio (y su empresa) cambiaron en la edicion
        negocio = _obtener_negocio(db, obj.id_negocio)
        if negocio:
            bd_articulo.id_emp = negocio.id_emp
        bd_articulo.id_categoria = obj.id_categoria
        bd_articulo.id_subcategoria = obj.id_subcategoria
        bd_articulo.id_unidad = obj.id_unidad
        bd_articulo.id_tiposervicio = obj.id_tiposervicio
        bd_articulo.id_impuesto = obj.id_impuesto
        bd_articulo.activo_stock = obj.activo_stock
        bd_articulo.maneja_lote = obj.maneja_lote
        bd_articulo.stock_min = obj.stock_min
        bd_articulo.stock_max = obj.stock_max
        bd_articulo.grupo_contable = obj.grupo_contable
        bd_articulo.cta_inventario = obj.cta_inventario
    
        bd_articulo.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        bd_articulo.fecha_mod = obj.fecha_mod

         # 2. Crear los codigos de barra para el model
        db.query(model_articulos.CodigosBarraModel).filter(model_articulos.CodigosBarraModel.id_articulo == id_articulo).delete()        
        db.flush()
         
        for i,codigos in enumerate(obj.codigosBarra, start=1):
            db_codigos = model_articulos.CodigosBarraModel(
                id_articulo=id_articulo,
                id_codbarra=codigos.id_codbarra or 0,
                linea=i, #Numerador de linea
                cod_barra=codigos.cod_barra,
                ref_barra=codigos.ref_barra,
                estado= codigos.estado,
                registro_nuevo=codigos.registro_nuevo
            )
            db.add(db_codigos)
        db.flush()
        
        db.execute(
                text("CALL public.sp_articulo_updatecodigosbarra(:p_id_articulo)"), 
                {"p_id_articulo": id_articulo}
            )   
            

        db.commit()
        db.refresh(bd_articulo)
        return bd_articulo

    except HTTPException:
        raise
    except Exception:
        # Se conserva el rollback (hay varios pasos antes del commit final), pero se
        # relanza la excepción original en vez de envolverla en un mensaje crudo: así
        # el manejador global (IntegrityError/DataError) responde con un mensaje amigable.
        db.rollback()
        raise


# Eliminar Articulo
def delete_articulo(db: Session, id_articulo: int):
    # 1. Buscamos el artículo para confirmar que existe
    bd_articulo = db.query(model_articulos.Articulo).filter(
        model_articulos.Articulo.id_articulo == id_articulo
    ).first()

    if not bd_articulo:
        # Si no existe, no hay nada que borrar
        return None

    try:
        # 2. Borramos los hijos primero
        db.query(model_articulos.CodigosBarra).filter(
            model_articulos.CodigosBarra.id_articulo == id_articulo
        ).delete()

        db.query(model_articulos.CodigosBarraModel).filter(
            model_articulos.CodigosBarraModel.id_articulo == id_articulo
        ).delete()

        # 3. Borramos el padre
        db.delete(bd_articulo)

        # 4. Guardamos cambios
        db.commit()

        return bd_articulo

    except Exception:
        # Se conserva el rollback (borrado en varios pasos), pero se relanza la
        # excepción original para que el manejador global de IntegrityError la
        # convierta en el mensaje de "registro en uso en otro módulo".
        db.rollback()
        raise