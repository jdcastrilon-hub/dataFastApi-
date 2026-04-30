from sqlalchemy import Column, Integer, Sequence, String, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Persona(Base):
    __tablename__ = "m_personas"
    __table_args__ = {"schema": "public"}

    id_persona = Column(Integer,Sequence('m_personas_id_persona_seq'), primary_key=True, index=True)
    id_tipodoc = Column(Integer, ForeignKey("public.m_tipodocumentos.id"), nullable=False)
    cod_tit = Column(String(50), unique=True, nullable=False)
    nombres = Column(String(60), nullable=False)
    apellidos = Column(String(60), nullable=False)
    nombre_completo = Column(String(120), nullable=False)
    sexo = Column(String(2), nullable=True)
    fec_nacimiento = Column(Date, nullable=True)
    direccion = Column(String(50), nullable=True)
    telefono = Column(String(60), nullable=True)
    mail = Column(String(60), nullable=True)
    id_ciudad = Column(Integer, nullable=False)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación opcional para traer datos del tipo de documento
    tipo_documento = relationship("TipoDocumento", back_populates="personas")

    #Relacion Proveedor
    proveedor= relationship("Proveedor", back_populates="persona") 
    cliente= relationship("Cliente", back_populates="persona") 
    