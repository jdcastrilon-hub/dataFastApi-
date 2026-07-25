from sqlalchemy import Boolean, Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
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
    id_emp = Column(Integer,ForeignKey("public.md_empresas.id_emp"), nullable=False)
    cod_sucursal = Column(String(20), nullable=False)
    nom_sucursal = Column(String(80), nullable=False)
    id_ciudad = Column(Integer, nullable=False)
    direccion = Column(String(60))
    telefono = Column(String(20))
    activo = Column(Boolean, nullable=False, default=True)
    logs = Column(JSON)
    fecha_mod = Column(DateTime, onupdate=func.now())

    #relaciones
    bodegas = relationship("Bodega", back_populates="sucursal")

    empresa =relationship("Empresa", back_populates="sucursales")

    caja = relationship("MCaja", back_populates="sucursal")

    usuarios = relationship("SucursalXUsuario", back_populates="sucursal", cascade="all, delete-orphan")


class SucursalXUsuario(Base):
    __tablename__ = "m_userxsucursal"
    __table_args__ = {"schema": "public"}

    id_sucursal = Column(Integer, ForeignKey("public.m_sucursales.id"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), primary_key=True)

    sucursal = relationship("Sucursal", back_populates="usuarios")
    usuario = relationship("Usuario")