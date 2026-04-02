from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import model_servicio 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_sericios(db: Session):
    return db.query(model_servicio.TipoServicio).all()