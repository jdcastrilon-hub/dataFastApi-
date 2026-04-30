from sqlalchemy import Column, Integer, Numeric, Sequence, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Cliente(Base): 
    __tablename__ = "m_clientes"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.m_empresa.id_emp"), nullable=False)
    id_cliente = Column(Integer,Sequence("m_clientes_id_cliente_seq"), primary_key=True, index=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("public.m_personas.id_persona"), nullable=False)
    cod_tit = Column(String(50), unique=True, nullable=False)
    nom_cliente = Column(String(100), nullable=False)
    activo = Column(String(2), nullable=False)
    observacion = Column(String(250), nullable=False)
    direccion = Column(String(50), nullable=False)
    mail = Column(String(60), nullable=False)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación para obtener datos de la persona asociada
    persona = relationship("Persona", back_populates="cliente")
    
 