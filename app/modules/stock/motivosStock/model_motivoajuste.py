from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class MotivoAjuste(Base):
    __tablename__ = "m_motivoajuste"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_motivo', name='m_motivoajuste_unique'),
        {"schema": "public"}
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    cod_motivo = Column(String(10), nullable=False)
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