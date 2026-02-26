from sqlalchemy import desc, or_
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

# Crear un Articulo
def create_articulo(db: Session, articulo: schema_articulos.ArticuloCreate):
    # Convertimos el schema a un diccionario y lo pasamos al modelo
    db_bodega = model_articulos.Articulo(**articulo.model_dump())
    
    db.add(db_bodega)
    db.commit()
    db.refresh(db_bodega) # Aquí se recupera el ID generado por el autonumérico
    return db_bodega