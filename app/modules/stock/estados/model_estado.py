from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base
import datetime
from app.database import Base

class Estado(Base):
    __tablename__ = "m_estados"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    cod_estado = Column(String(20), unique=True, nullable=False)
    nom_estado = Column(String(80), nullable=False)
    activo = Column(String(2), nullable=False)
    loteable = Column(String(2), nullable=False)
    tiene_ubicaciones = Column(String(2), nullable=False)
    unidades_negativas = Column(String(2), nullable=False)
    obervacion = Column(String(250), nullable=False) # Mantengo el typo del SQL original
    # Auditoría
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    logs = Column(JSON, nullable=True)