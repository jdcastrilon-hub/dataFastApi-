from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, JSON, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class ConfComercial(Base):
    __tablename__ = "m_confcomercial"
    # Rol/Bodega (relaciones de abajo) estan registradas con schema="public"
    # explicito en sus propios modelos - sin esto aca, SQLAlchemy no puede
    # resolver el join automatico entre 'm_confcomercial' y 'public.m_bodegas'.
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    precio_cero_editable = Column(Boolean, nullable=False, default=False)
    # Placeholders sin funcionalidad propia todavia (reimpresion de factura,
    # devolucion de venta) - agregados a peticion explicita para no migrar de
    # nuevo cuando esas pantallas se construyan.
    reimpresion_factura_permitida = Column(Boolean, nullable=False, default=False)
    # Sin prefijo "public." a proposito: model_bodega.py declara __table_args__
    # dos veces (schema="public" primero, un UniqueConstraint despues que lo
    # pisa sin querer), asi que la tabla real queda registrada como "m_bodegas"
    # a secas pese a lo que el codigo de ese archivo parece decir.
    id_bodega_devoluciones = Column(Integer, ForeignKey("m_bodegas.id"), nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    bodega_devoluciones = relationship("Bodega")


class ConfComercialDctoRol(Base):
    __tablename__ = "m_confcomercial_dctoxrol"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("public.md_rol.id_rol"), primary_key=True)
    max_descuento = Column(Numeric(5, 2), nullable=False)

    rol = relationship("Rol")
