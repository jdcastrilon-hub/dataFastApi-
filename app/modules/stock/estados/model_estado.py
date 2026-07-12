from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Estado(Base):
    __tablename__ = "m_estados"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, nullable=False)
    cod_estado = Column(String(20), unique=True, nullable=False)
    nom_estado = Column(String(80), nullable=False)
    activo = Column(Boolean, nullable=False)
    obervacion = Column(String(250), nullable=False) # Mantengo el typo del SQL original
    # Auditoría
    fecha_mod = Column(DateTime, nullable=True)
    logs = Column(JSON, nullable=True)

    #relaciones
    ajustes = relationship(
        "AjusteStock",
        back_populates="estado",
        primaryjoin="Estado.id == AjusteStock.id_estado"
    )
    traslados_origen = relationship(
        "TrasladoStock",
        back_populates="estado_origen",
        foreign_keys="TrasladoStock.id_estado_origen"
    )
    traslados_destino = relationship(
        "TrasladoStock",
        back_populates="estado_destino",
        foreign_keys="TrasladoStock.id_estado_destino"
    )
