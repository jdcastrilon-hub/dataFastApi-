from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class MListaPrecio(Base):
    __tablename__ = "m_listaprecio"

    id_lista = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    nombre = Column(String, nullable=False)
    # Nullable a proposito: null = lista base (General u otra base), con valor =
    # lista negociada especifica de ese cliente. Ver project_data_lista_precios_design.
    id_cliente = Column(Integer, ForeignKey("public.m_clientes.id_cliente"), nullable=True)
    # Identifica sin ambiguedad cual es LA lista general de la empresa (a la que se
    # anclan las reglas de precio por categoria). Un indice unico parcial en BD
    # (ux_listaprecio_general_por_emp) ya garantiza una sola por empresa.
    es_general = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    cliente = relationship("Cliente")
    usuarios = relationship("MListaPrecioXUser", back_populates="lista", cascade="all, delete-orphan")


class MListaPrecioXUser(Base):
    __tablename__ = "m_listaprecioxuser"

    # Solo aplica a listas base (id_cliente IS NULL); una lista "General" no
    # necesita filas aca (acceso implicito para todos). Ver design doc.
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), primary_key=True)
    id_lista = Column(Integer, ForeignKey("m_listaprecio.id_lista"), primary_key=True)

    lista = relationship("MListaPrecio", back_populates="usuarios")
    usuario = relationship("Usuario")
