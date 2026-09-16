from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class MedioPago(Base):
    __tablename__ = "m_mediopagos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, nullable=False)
    tipo = Column(String(20), nullable=False)
    orden = Column(Integer, nullable=True)
    id_emp = Column(Integer, nullable=False)
    # Nullable: solo aplica a medios de pago que liquidan en una cuenta bancaria
    # fija (Transferencia, Tarjeta) - Efectivo queda sin banco porque el destino
    # ya se resuelve por la caja de la venta (ver project_data_tesoreria_module).
    id_banco = Column(Integer, ForeignKey("m_banco.id"), nullable=True)
    fecha_mod = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    banco = relationship("Banco")
