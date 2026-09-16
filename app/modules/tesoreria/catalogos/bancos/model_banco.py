from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Banco(Base):
    __tablename__ = "m_banco"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_banco', name='m_banco_unique'),
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, nullable=False)
    cod_banco = Column(String(10), nullable=False)
    nom_banco = Column(String(100), nullable=False)
    nro_cuenta = Column(String(30), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, nullable=True)

    usuarios = relationship("BancoXUser", back_populates="banco", cascade="all, delete-orphan")


class BancoXUser(Base):
    __tablename__ = "m_bancoxuser"

    id = Column(Integer, primary_key=True, index=True)
    id_banco = Column(Integer, ForeignKey("m_banco.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), nullable=False)

    banco = relationship("Banco", back_populates="usuarios")
    usuario = relationship("Usuario")
