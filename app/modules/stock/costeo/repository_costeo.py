from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import model_costeo 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_costeo(db: Session):
    return db.query(model_costeo.Costeo).all()