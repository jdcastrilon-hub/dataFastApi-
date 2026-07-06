from sqlalchemy import Boolean, Column, ForeignKey, Integer, PrimaryKeyConstraint, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Empresa(Base):
    __tablename__ = "md_empresas"
    __table_args__ = {'schema': 'public'}

    # Definición de columnas basadas en tu script SQL
    id_emp = Column(Integer, primary_key=True, autoincrement=True)
    nom_emp = Column(String(50), nullable=False)
    razon_social = Column(String(50), nullable=False)
    cod_doc = Column(String(5), nullable=False)
    nit = Column(String(20), nullable=False)
    direccion = Column(String(50), nullable=False)
    cod_ciudad = Column(Integer, nullable=False)
    telefono = Column(String(15), nullable=False)
    correo = Column(String(50), nullable=False)
    
    # Campo para almacenar la lista de objetos JSON (logs)
    logs = Column(JSON, nullable=True)
    
    # Campo de fecha que se actualiza automáticamente
    fecha_mod = Column(DateTime, onupdate=func.now())

    # Relacion de Negocio -> Empresa
    negocios = relationship("Negocio", back_populates="empresa")
    compras = relationship("Compra", back_populates="empresa")
    proveedor = relationship("Proveedor", back_populates="empresa")
    sucursales = relationship("Sucursal", back_populates="empresa")
    usuarios = relationship("EmpresaXUser", back_populates="empresa")

class EmpresaXUser(Base):
    __tablename__ = 'md_empresaxuser'
    __table_args__ = (
        PrimaryKeyConstraint('id_usuario', 'id_emp', name='md_empresaxuser_pkey'),
        {'schema': 'public'}  # Opcional: define el esquema si es necesario
    )

    id_usuario = Column(Integer, ForeignKey('public.md_usuarios.id_usuario', onupdate='NO ACTION', ondelete='NO ACTION'), nullable=False)
    id_emp = Column(Integer, ForeignKey('public.md_empresas.id_emp', onupdate='NO ACTION', ondelete='NO ACTION'), nullable=False)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="usuarios")