from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class MotivoAjuste(Base):
    __tablename__ = "m_motivoajuste"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    cod_motivo = Column(String(10), unique=True, nullable=False)
    nom_motivo = Column(String(80), nullable=False)
    signo = Column(Integer, nullable=False)
    activo = Column(String(2), nullable=False)
    cta_inventario = Column(String(15), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    logs = Column(JSON, nullable=True)

    #Relaciones
    ajustes = relationship(
        "AjusteStock", 
        back_populates="motivo",
        primaryjoin="MotivoAjuste.id == AjusteStock.id_motivo"
    )