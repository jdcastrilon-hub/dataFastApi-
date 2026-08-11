from sqlalchemy import Column, Integer, Numeric, String, JSON, DateTime, ForeignKey, UniqueConstraint
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


# Catalogo global de tipos de impuesto (IVA, IVA2, ...): no tiene CRUD propio,
# es solo lectura para alimentar el combo "Tipo de Impuesto" del formulario.
class TipoImpuesto(Base):
    __tablename__ = 'm_tipoimpuesto'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    tipoimpu = Column(String(20), nullable=False)
    nombre_impuesto = Column(String(80), nullable=False)


class Impuesto(Base):
    __tablename__ = 'm_impuesto'
    __table_args__ = (
        UniqueConstraint('id_emp', 'tasa_impu', name='impuestos_pk_unic'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_emp = Column(Integer, ForeignKey('public.md_empresas.id_emp'), nullable=False)
    id_tipo = Column(Integer, ForeignKey('public.m_tipoimpuesto.id'), nullable=True)
    tasa_impu = Column(String(10), nullable=False)
    nombre_tasa = Column(String(50), nullable=False)
    es_exenta = Column(String(2), nullable=False)
    porc_tasa = Column(Numeric, nullable=False)
    imp_minimo = Column(Numeric, nullable=False)
    cuenta_vta = Column(String(15), nullable=False)
    cuenta_cmp = Column(String(15), nullable=False)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    tipo_impuesto = relationship("TipoImpuesto")
    # Relación hacia Artículos
    # (Un tipo de costeo puede aplicarse a muchos artículos)
    articulos = relationship("Articulo", back_populates="impuesto")
    # Referencia para compras
    compras = relationship("DetalleCompra", back_populates="detalleimpuesto1")

    def __repr__(self):
        return f"<MImpuesto(id={self.id}, nombre='{self.nombre_tasa}')>"