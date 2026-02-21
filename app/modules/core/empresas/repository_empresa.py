from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import model_empresa 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_empresas(db: Session):
    return db.query(model_empresa.Empresa).all()

def get_empresasByNegocios(db: Session):
    return db.query(model_empresa.Empresa).options(
        joinedload(model_empresa.Empresa.negocios)).all()