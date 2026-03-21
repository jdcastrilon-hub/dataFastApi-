from sqlalchemy import desc, exists, false, or_, text
from sqlalchemy.orm import Session , joinedload
from . import model_articulos , schema_articulos

# Obtener todas las bodegas ordenadas de mayor a menor
def get_articulos(db: Session):
    return db.query(model_articulos.Articulo).all()

def get_articulosCompleto(db: Session):
    return db.query(model_articulos.Articulo).options(joinedload(model_articulos.Articulo.negocio),
                                                      joinedload(model_articulos.Articulo.subcategoria),
                                                      joinedload(model_articulos.Articulo.unidad)
                                                       ).all()

def find_codigoBarra_by_query(db: Session, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"
        
        return (
            db.query(
                model_articulos.CodigosBarra.id_articulo.label("idArticulo"),
                model_articulos.CodigosBarra.id_codbarra.label("idCodBarra"),
                model_articulos.CodigosBarra.cod_barra.label("codArticulo"),
                model_articulos.CodigosBarra.ref_barra.label("nomArticulo")
            )
            .filter(
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
                model_articulos.Articulo.nom_articulo.label("nomArticulo")
            )
            .filter(
                or_(
                    model_articulos.Articulo.cod_articulo.ilike(search_filter),
                    model_articulos.Articulo.nom_articulo.ilike(search_filter)
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


# Crear un Articulo
def create_articulo(db: Session, articulo: schema_articulos.ArticuloCreate):

    # Usamos exclude={"codigosBarra"} para que no choque con la relación de SQLAlchemy
    datos_articulo = articulo.model_dump(exclude={"codigosBarra"})
    # Convertimos el schema a un diccionario y lo pasamos al modelo
    bd_articulo = model_articulos.Articulo(**datos_articulo)
    
    db.add(bd_articulo)
    db.flush()

    # 2. Crear los codigos de barra
    for codigos in articulo.codigosBarra:
        db_codigos = model_articulos.CodigosBarra(
            id_articulo=bd_articulo.id_articulo,
            cod_barra=codigos.cod_barra,
            ref_barra=codigos.ref_barra
        )
        db.add(db_codigos)

    db.commit()
    db.refresh(bd_articulo) 
    return bd_articulo

