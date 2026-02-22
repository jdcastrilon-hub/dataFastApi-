from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import model_unidad 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_unidades(db: Session):
    return db.query(model_unidad.Unidad).all()