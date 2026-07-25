from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from app.database import Base

class Rol(Base):
    __tablename__ = "md_rol"
    __table_args__ = {"schema": "public"}

    id_rol = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    codigo = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_mod = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(JSON, nullable=True)
    # Rol "dueño"/superadmin: si es True, salta por completo el chequeo de
    # md_rol_permiso (acceso total a todo, incluyendo formularios futuros que
    # todavia no existen). Deliberadamente NO expuesto en ningun schema/endpoint
    # de escritura - se activa solo directo en Postgres al dar de alta una
    # empresa, nunca desde el formulario de Roles.
    es_superadmin = Column(Boolean, nullable=False, default=False)

    usuarios = relationship("RolXUsuario", back_populates="rol", cascade="all, delete-orphan")


class RolXUsuario(Base):
    __tablename__ = "md_usuarioxrol"
    __table_args__ = {"schema": "public"}

    # Clave primaria compuesta ya existente en la BD (id_usuario, id_rol) - sin id propio.
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("public.md_rol.id_rol"), primary_key=True)

    rol = relationship("Rol", back_populates="usuarios")
    usuario = relationship("Usuario")
