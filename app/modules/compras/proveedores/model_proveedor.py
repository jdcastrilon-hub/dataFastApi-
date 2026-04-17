from sqlalchemy import Column, Integer, Numeric, Sequence, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Proveedor(Base): 
    __tablename__ = "m_proveedores"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.m_empresa.id_emp"), nullable=False)
    id_proveedor = Column(Integer,Sequence("m_proveedores_id_proveedor_seq"), primary_key=True, index=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("public.m_personas.id_persona"), nullable=False)
    cod_tit = Column(String(50), unique=True, nullable=False)
    razon_social = Column(String(150), nullable=False)
    regimen = Column(String(20), nullable=False)
    activo = Column(String(2), nullable=False)
    observacion = Column(String(250), nullable=False)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación para obtener datos de la persona asociada
    persona = relationship("Persona", back_populates="proveedor")
    compras = relationship("Compra", back_populates="proveedor")  
 