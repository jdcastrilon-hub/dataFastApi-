from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_medio , schema_medio
from app.modules.comercial.mediopago import model_medio

# Obtener todas las bodegas ordenadas de mayor a menor
def get_medios_pago(db: Session):
    return db.query(model_medio.MedioPago).order_by(model_medio.MedioPago.orden).all()