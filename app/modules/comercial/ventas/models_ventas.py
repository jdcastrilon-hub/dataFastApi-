from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, Numeric, PrimaryKeyConstraint, Sequence, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, foreign
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
    imp_ingreso = Column(Numeric(14, 2), nullable=False)
    imp_vuelto = Column(Numeric(14, 2), nullable=False)
    # Nullable: solo aplica cuando el usuario tiene un turno/caja POS abierto en el
    # momento de vender (venta-pos siempre, venta-directa a veces). Si no hay turno
    # abierto (ej. un administrador haciendo una venta de backoffice), la venta queda
    # sin turno y en cambio se guarda id_caja (la caja elegida manualmente, ver abajo).
    id_turno = Column(Integer, nullable=True)
    # Nullable: solo se usa cuando NO hay turno abierto (ver id_turno) - registra
    # manualmente cual caja (de las asociadas al usuario via m_cajasxuser) se uso.
    # Si hay turno abierto, la caja ya se sabe indirectamente via id_turno -> m_cajas.
    id_caja = Column(Integer, nullable=True)
    fec_venc = Column(Date, nullable=False)
    id_moneda = Column(Integer, nullable=False)
    id_bodega = Column(Integer, nullable=False)
    id_estado = Column(Integer, nullable=False)
    vista = Column(String(16), nullable=False)
    signo = Column(Integer, nullable=False)
    
    # Totales e Impuestos
    imp_neto = Column(Numeric(14, 2), nullable=False)
    # Tipo de descuento aplicado ('No Aplica'/'General'/'Detalle') - la columna ya
    # existia en la tabla real pero nunca se habia mapeado en el modelo, asi que
    # aunque el frontend siempre la mandaba, Pydantic la descartaba en silencio por
    # no estar declarada en el schema (nunca llegaba ni al modelo ni a la BD).
    tipo_dcto = Column(String(10), nullable=True)
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

    # Lineas de pago (reemplaza a las viejas columnas forma_pago/id_pago de la
    # cabecera - una venta puede pagarse con mas de un medio de pago, ej.
    # Efectivo + Transferencia. sp_comercial_ventapos lee de esta tabla en vez
    # de un solo id_pago fijo, mismo patron ya usado por td_cierreturno.
    detalles_pago = relationship(
        "FacturaMedioPago",
        back_populates="cabecera",
        primaryjoin="and_(Factura.id_emp == FacturaMedioPago.id_emp, Factura.id_trans == FacturaMedioPago.id_trans)",
        foreign_keys="[FacturaMedioPago.id_emp, FacturaMedioPago.id_trans]",
        cascade="all, delete-orphan"
    )

    # id_cliente/id_bodega no tienen FK declarada en la tabla real (igual que otras
    # tablas de este proyecto, ver project_data_crud_template) - relaciones viewonly
    # con join explicito, solo para poder traer el nombre en listados/edicion.
    cliente = relationship(
        "Cliente",
        primaryjoin="Factura.id_cliente == foreign(Cliente.id_cliente)",
        viewonly=True,
        uselist=False
    )
    bodega = relationship(
        "Bodega",
        primaryjoin="Factura.id_bodega == foreign(Bodega.id)",
        viewonly=True,
        uselist=False
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
    # Nombre del articulo al momento de la venta (snapshot para mostrarlo al
    # ver/editar despues, mismo concepto que td_compras.ref_compras pero con
    # nombre propio para no mezclar terminologia entre modulos). Nullable
    # porque las filas historicas anteriores a esta columna no lo tienen.
    referencia = Column(String(100), nullable=True)
    precio_unit = Column(Numeric(14, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
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
    imp_neto= Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)

    

    # Relación inversa
    cabecera = relationship(
        "Factura",
        back_populates="detalles",
        primaryjoin="and_(Factura.id_emp == FacturaDetalle.id_emp, Factura.id_trans == FacturaDetalle.id_trans)",
        foreign_keys="[FacturaDetalle.id_emp, FacturaDetalle.id_trans]"
    )


class FacturaMedioPago(Base):
    __tablename__ = "td_facturas_mediopago"
    __table_args__ = {"schema": "public"}

    # id propio (no se reutiliza en ningun otro lado, a diferencia de id_trans
    # de la cabecera) - mismo criterio que td_cierreturno.id.
    id = Column(Integer, primary_key=True)
    id_emp = Column(Integer, nullable=False)
    id_trans = Column(Integer, nullable=False)
    linea = Column(Integer, nullable=True)  # Solo como referencia.
    id_mediopago = Column(Integer, ForeignKey("public.m_mediopagos.id"), nullable=False)
    importe = Column(Numeric(14, 2), nullable=False, default=0)

    mediopago = relationship("MedioPago")

    cabecera = relationship(
        "Factura",
        back_populates="detalles_pago",
        primaryjoin="and_(Factura.id_emp == FacturaMedioPago.id_emp, Factura.id_trans == FacturaMedioPago.id_trans)",
        foreign_keys="[FacturaMedioPago.id_emp, FacturaMedioPago.id_trans]"
    )