from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, Numeric, JSON, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class DevolucionCompra(Base):
    __tablename__ = "t_devolucioncompras"
    __table_args__ = {"schema": "public"}

    # Misma secuencia 'id_transaccion' que comparten compras/ajustes/traslados
    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("public.m_sucursales.id"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("public.m_proveedores.id_proveedor"), nullable=False)
    id_compra_origen = Column(BigInteger, ForeignKey("public.t_compras.id_trans"), nullable=False)
    id_bodega = Column(Integer, ForeignKey("m_bodegas.id"), nullable=False)
    id_estado = Column(Integer, nullable=False)

    fec_doc = Column(Date, nullable=False)
    documento = Column(String(16), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    id_motivo = Column(Integer, ForeignKey("public.m_motivodevolucion.id"), nullable=False)
    observacion = Column(String(250), nullable=False)
    # Reservado para un futuro flujo de autorizacion (Pendiente/Aprobada/Rechazada).
    # Hoy no tiene ninguna logica: la devolucion impacta stock/costos de inmediato al guardar.
    status = Column(String(2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    # Relaciones
    proveedor = relationship("Proveedor")
    compra_origen = relationship("Compra")
    bodega = relationship("Bodega")
    motivo = relationship("MotivoDevolucion")
    detalles = relationship("DetalleDevolucionCompra", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DevolucionCompra(id_trans={self.id_trans}, nro_docum={self.nro_docum})>"


class DetalleDevolucionCompra(Base):
    __tablename__ = "td_devolucioncompras"
    __table_args__ = {"schema": "public"}

    id_trans = Column(BigInteger, ForeignKey("public.t_devolucioncompras.id_trans"), primary_key=True)
    linea = Column(Integer, primary_key=True)

    id_articulo = Column(Integer, nullable=False)
    id_codbarra = Column(Integer, nullable=False)
    id_lote = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unit = Column(Numeric(14, 2), nullable=False)
    costo_total = Column(Numeric(14, 2), nullable=False)

    parent = relationship("DevolucionCompra", back_populates="detalles")
    # Relacion de solo lectura (sin back_populates, sin tocar el modelo compartido
    # CodigosBarra): igual que td_compras, id_codbarra no tiene una FK real en la
    # BD (no es unica por si sola en m_artxcodigobarra).
    articulo = relationship(
        "CodigosBarra",
        primaryjoin="DetalleDevolucionCompra.id_codbarra == CodigosBarra.id_codbarra",
        foreign_keys=[id_codbarra],
        viewonly=True
    )
