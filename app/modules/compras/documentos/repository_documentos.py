from sqlalchemy.orm import Session
from . import model_documentos , schema_documentos

# Obtener todas las bodegas ordenadas de mayor a menor
def get_documentos(db: Session):
    return db.query(model_documentos.TipoDocumento).all()