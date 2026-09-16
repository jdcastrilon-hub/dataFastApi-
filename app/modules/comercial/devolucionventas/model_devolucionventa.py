import datetime
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, Sequence, String
from sqlalchemy.orm import relationship
from app.database import Base


class NotaFactura(Base):
    __tablename__ = "t_notafactura"
    __table_args__ = {"schema": "public"}

    # Misma secuencia 'id_transaccion' que comparten compras/ajustes/traslados/
    # devoluciones/facturas - por eso id_trans_ref puede ser FK real hacia
    # t_facturas aunque el origen sea otra tabla, sin duplicar numeracion.
    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    id_cliente = Column(Integer, nullable=False)
    id_sucursal = Column(Integer, ForeignKey("public.m_sucursales.id"), nullable=False)
    # La factura que se esta devolviendo. Tiene FK compuesta real en la BD
    # (id_emp, id_trans_ref) -> t_facturas(id_emp, id_trans) - ver migracion
    # a4579791d53f. No se declara aca como ForeignKey de columna simple porque
    # t_facturas tiene llave compuesta; se resuelve con el relationship de abajo.
    id_trans_ref = Column(BigInteger, nullable=False)
    id_bodega = Column(Integer, ForeignKey("m_bodegas.id"), nullable=False)
    id_estado = Column(Integer, nullable=False)
    # Nullable: solo se llenan cuando el motivo elegido tiene devuelve_dinero=true
    # (reembolso real de caja). Sin FK declarada, mismo criterio que
    # t_facturas.id_turno/id_caja (tampoco tienen FK real en la BD).
    id_turno = Column(Integer, nullable=True)
    id_caja = Column(Integer, nullable=True)

    fec_doc = Column(Date, nullable=False)
    # Identidad propia de ESTA nota (su propio numerador) - no confundir con
    # id_trans_ref (a que factura referencia).
    documento = Column(String(16), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    serie_docum = Column(String(8), nullable=False)

    id_motivo = Column(Integer, ForeignKey("public.m_motivodevolucionventa.id"), nullable=False)
    observacion = Column(String(250), nullable=True)

    imp_neto = Column(Numeric(14, 2), nullable=False)
    impuesto1 = Column(String(6), nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    impuesto2 = Column(String(6), nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    impuesto3 = Column(String(6), nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)

    vista = Column(String(16), nullable=False)
    # Reservado para un futuro flujo de autorizacion, mismo criterio que
    # t_devolucioncompras.status - hoy sin logica, la nota impacta de inmediato.
    status = Column(String(2), nullable=False)

    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    bodega = relationship("Bodega")
    motivo = relationship("MotivoDevolucionVenta")
    detalles = relationship("DetalleNotaFactura", back_populates="cabecera", cascade="all, delete-orphan")

    # id_cliente/id_trans_ref no tienen FK real declarada aca (aunque id_trans_ref
    # SI la tiene en la BD, ver arriba) - se resuelven por join explicito viewonly,
    # mismo criterio ya usado en el resto del proyecto (ver project_data_crud_template).
    cliente = relationship(
        "Cliente",
        primaryjoin="NotaFactura.id_cliente == foreign(Cliente.id_cliente)",
        viewonly=True,
        uselist=False
    )
    factura_origen = relationship(
        "Factura",
        primaryjoin="and_(NotaFactura.id_emp == foreign(Factura.id_emp), NotaFactura.id_trans_ref == foreign(Factura.id_trans))",
        viewonly=True,
        uselist=False
    )


class DetalleNotaFactura(Base):
    __tablename__ = "td_notafactura"
    __table_args__ = {"schema": "public"}

    id_trans = Column(BigInteger, ForeignKey("public.t_notafactura.id_trans"), primary_key=True)
    linea = Column(Integer, primary_key=True)

    id_articulo = Column(Integer, nullable=False)
    id_codbarra = Column(Integer, nullable=False)
    id_lote = Column(Integer, nullable=False, default=0)
    cantidad = Column(Integer, nullable=False)
    precio_unit = Column(Numeric(14, 2), nullable=False)

    impuesto1 = Column(String(6), nullable=False)
    id_tasaimp1 = Column(Integer, nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    impuesto2 = Column(String(6), nullable=False)
    id_tasaimp2 = Column(Integer, nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    impuesto3 = Column(String(6), nullable=False)
    id_tasaimp3 = Column(Integer, nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)

    imp_neto = Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)

    cabecera = relationship("NotaFactura", back_populates="detalles")
    # Igual que td_compras/td_facturas: id_codbarra no tiene FK real (no es unica
    # por si sola en m_artxcodigobarra).
    articulo = relationship(
        "CodigosBarra",
        primaryjoin="DetalleNotaFactura.id_codbarra == foreign(CodigosBarra.id_codbarra)",
        viewonly=True
    )
