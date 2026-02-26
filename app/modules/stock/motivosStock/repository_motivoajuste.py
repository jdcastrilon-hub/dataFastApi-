from sqlalchemy.orm import Session
from . import model_motivoajuste ,schema_ajuste

def get_all(db: Session):
        return db.query(model_motivoajuste.MotivoAjuste).all()

   