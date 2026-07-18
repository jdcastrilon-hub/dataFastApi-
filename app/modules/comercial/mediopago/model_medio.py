from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base

class MedioPago(Base):
    __tablename__ = "m_mediopagos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, nullable=False)
    tipo = Column(String(20), nullable=False)
    orden = Column(Integer, nullable=True)
    id_emp = Column(Integer, nullable=False)
    fecha_mod = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)
