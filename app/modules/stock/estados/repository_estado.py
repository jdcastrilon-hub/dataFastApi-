from sqlalchemy.orm import Session
from . import model_estado , schema_estado

# Obtener todas las bodegas 
def get_estados(db: Session):
    return db.query(model_estado.Estado).all()