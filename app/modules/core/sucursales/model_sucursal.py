from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Sucursal(Base):
    __tablename__ = "m_sucursales"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_sucursal', name='m_sucursales_unique'),
        {'schema': 'public'} 
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, nullable=False)
    cod_sucursal = Column(String(20), nullable=False)
    nom_sucursal = Column(String(80), nullable=False)
    id_ciudad = Column(Integer, nullable=False)
    direccion = Column(String(60))
    telefono = Column(String(20))
    activo = Column(String(2), nullable=False, default="SI")
    logs = Column(JSON)
    fecha_mod = Column(DateTime, onupdate=func.now())

    #relaciones
    bodegas = relationship("Bodega", back_populates="sucursal")