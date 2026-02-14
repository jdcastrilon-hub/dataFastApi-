from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from app.database import Base
from sqlalchemy.sql import func

class Bodega(Base):
    __tablename__ = "m_bodegas"

    id = Column(Integer, primary_key=True, index=True)
    id_sucursal = Column(Integer,  nullable=False) 
    cod_bodega = Column(String(20), nullable=False)
    nom_bodega = Column(String(80), nullable=False)
    principal = Column(String(2), nullable=False)
    tiene_ubicaciones = Column(String(2), nullable=False)
    activo = Column(String(2), nullable=False)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, onupdate=func.now(), nullable=True)

    # Definimos la restricción UNIQUE que tienes en el SQL
    __table_args__ = (
        UniqueConstraint('id_sucursal', 'cod_bodega', name='m_bodegas_unique'),
    )