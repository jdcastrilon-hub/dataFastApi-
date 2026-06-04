from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, Numeric, PrimaryKeyConstraint, Sequence, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Factura(Base):
    __tablename__ = "t_facturas"
    __table_args__ = {"schema": "public"}

    # Llave Primaria Compuesta
    id_emp = Column(Integer, primary_key=True)
    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)
    
    # Datos de Relación y Ubicación
    id_cliente = Column(Integer, nullable=False)
    id_sucursal_emp = Column(Integer, nullable=False)
    id_sucursal_cliente = Column(Integer, nullable=False)
    id_bodega = Column(Integer, nullable=False)
    
    # Documentación
    fec_doc = Column(Date, nullable=False)
    documento = Column(String(16), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    serie_docum = Column(String(8), nullable=False)
    
    # Referencias y Remitos
    documento_ref = Column(String(16), nullable=False)
    nro_ref = Column(Integer, nullable=False)
    serie_ref = Column(String(8), nullable=False)
    documento_remito = Column(String(16), nullable=False)
    nro_remito = Column(Integer, nullable=False)
    serie_remito = Column(String(8), nullable=False)
    
    # Información Comercial
    observacion = Column(String(250), nullable=False)
    id_pago = Column(Integer, nullable=False)
    fec_venc = Column(Date, nullable=False)
    id_moneda = Column(Integer, nullable=False)
    id_estado = Column(Integer, nullable=False)
    vista = Column(String(16), nullable=False)
    signo = Column(Integer, nullable=False)
    
    # Totales e Impuestos
    imp_neto = Column(Numeric(14, 2), nullable=False)
    porc_dcto = Column(Numeric(14, 2), nullable=False)
    imp_descuento = Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)
    
    impuesto1 = Column(String(6), nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    impuesto2 = Column(String(6), nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    impuesto3 = Column(String(6), nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)

    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    # Relación con el detalle    
    detalles = relationship(
        "FacturaDetalle", 
        back_populates="cabecera",
        primaryjoin="and_(Factura.id_emp == FacturaDetalle.id_emp, Factura.id_trans == FacturaDetalle.id_trans)",
        foreign_keys="[FacturaDetalle.id_emp, FacturaDetalle.id_trans]"
    )


class FacturaDetalle(Base):
    __tablename__ = "td_facturas"

    # Llaves Primarias y Foráneas (Compuestas)
    id_emp = Column(Integer, ForeignKey("public.t_facturas.id_emp"), primary_key=True)
    id_trans = Column(Integer, ForeignKey("public.t_facturas.id_trans"), primary_key=True)
    id_articulo = Column(Integer, primary_key=True)
    linea = Column(Integer, primary_key=True)
    
    # Datos del Producto
    id_codbarra = Column(Integer, nullable=False)
    precio_unit = Column(Numeric(14, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    id_lote = Column(Integer, nullable=False)
    tipo_vta = Column(String(2), nullable=False)
    
    # Impuestos por Línea
    impuesto1 = Column(String(6), nullable=False)
    id_tasaimp1 = Column(Integer, nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    
    impuesto2 = Column(String(6), nullable=False)
    id_tasaimp2 = Column(Integer, nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    
    impuesto3 = Column(String(6), nullable=False)
    id_tasaimp3 = Column(Integer, nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)
    
    # Descuentos y Totales por Línea
    porc_dcto = Column(String(62), nullable=False)
    imp_dcto = Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)

    

    # Relación inversa
    cabecera = relationship(
        "Factura", 
        back_populates="detalles",
        primaryjoin="and_(Factura.id_emp == FacturaDetalle.id_emp, Factura.id_trans == FacturaDetalle.id_trans)",
        foreign_keys="[FacturaDetalle.id_emp, FacturaDetalle.id_trans]"
    )