from sqlalchemy.orm import Session
from . import modelo_personas 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_personas(db: Session):
    return db.query(modelo_personas.Persona).all()