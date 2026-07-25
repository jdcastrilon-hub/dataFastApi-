from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class MConceptoCaja(Base):
    __tablename__ = "m_conceptoscaja"

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    nom_concepto = Column(String(100), nullable=False)
    signo = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    aplica_limit = Column(Boolean, nullable=True, default=False)
    imp_limit = Column(Numeric, nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    usuarios = relationship("MConceptoCajaXUser", back_populates="concepto", cascade="all, delete-orphan")


class MConceptoCajaXUser(Base):
    __tablename__ = "m_conceptoscajaxuser"

    id = Column(Integer, primary_key=True, index=True)
    id_concepto = Column(Integer, ForeignKey("m_conceptoscaja.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), nullable=False)

    concepto = relationship("MConceptoCaja", back_populates="usuarios")
    usuario = relationship("Usuario")
