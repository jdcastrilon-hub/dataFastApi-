from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import modal_impuesto 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_impuestos(db: Session):
    return db.query(modal_impuesto.Impuesto).all()