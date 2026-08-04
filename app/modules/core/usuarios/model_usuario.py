from sqlalchemy import Boolean, Column, Integer, Numeric, Sequence, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Usuario(Base): 
    __tablename__ = "md_usuarios"
    __table_args__ = {"schema": "public"}

    id_usuario= Column(Integer,  primary_key=True, index=True, nullable=False)
    usuario = Column(String(20),  nullable=False)    
    clave = Column(String(100), nullable=False)    
    id_persona = Column(Integer, ForeignKey("public.m_personas.id_persona"), nullable=False)
    nom_usuario = Column(String(100),nullable=False)
    activo = Column(Boolean, nullable=False)
    # Empresa que el login toma por defecto (ver controller_auth.py::login). Nullable
    # a proposito: si es NULL, o el usuario ya no tiene acceso activo a ella, el
    # login cae al comportamiento anterior (primera empresa activa encontrada).
    id_emp_principal = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=True)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación para obtener datos de la persona asociada
    persona = relationship("Persona", back_populates="user")
    
 