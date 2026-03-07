from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import models 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_ciudades(db: Session):
    return db.query(models.Ciudad).all()