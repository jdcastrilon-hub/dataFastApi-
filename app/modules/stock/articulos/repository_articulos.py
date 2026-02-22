from sqlalchemy import desc
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
# Crear un Articulo
def create_articulo(db: Session, articulo: schema_articulos.ArticuloCreate):
    # Convertimos el schema a un diccionario y lo pasamos al modelo
    db_bodega = model_articulos.Articulo(**articulo.model_dump())
    
    db.add(db_bodega)
    db.commit()
    db.refresh(db_bodega) # Aquí se recupera el ID generado por el autonumérico
    return db_bodega