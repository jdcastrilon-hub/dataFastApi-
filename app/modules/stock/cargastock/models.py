from sqlalchemy import Column, Integer, Sequence, String, BigInteger, Date, DateTime, JSON, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CargaStock(Base):
    __tablename__ = "t_cargastock"

    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    id_negocio = Column(Integer, ForeignKey("public.m_negocios.id"), nullable=False)
    id_bodega = Column(Integer, ForeignKey("m_bodegas.id"), nullable=False)
    id_estado = Column(Integer, ForeignKey("public.m_estados.id"), nullable=False)
    id_proveedor = Column(Integer, nullable=False)
    documento = Column(String(10), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    fecha_movimiento = Column(Date, nullable=False)
    observacion = Column(String(250))
    nombre_archivo = Column(String(150))
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, nullable=False)
    logs = Column(JSON)

    # passive_deletes=True: el borrado de detalles ya se hace a mano (ver
    # delete_carga_stock) porque id_trans es parte de la llave primaria compuesta de
    # DetalleCargaStock — el intento por defecto de SQLAlchemy de "poner en null" esa
    # columna al borrar la cabecera falla porque no se puede anular una PK.
    detalles = relationship("DetalleCargaStock", back_populates="cabecera", passive_deletes=True)
    bodega = relationship("Bodega", foreign_keys=[id_bodega])
    estado = relationship("Estado", foreign_keys=[id_estado])


class DetalleCargaStock(Base):
    __tablename__ = "td_cargastock"

    id_trans = Column(BigInteger, ForeignKey("t_cargastock.id_trans"), primary_key=True)
    id_articulo = Column(Integer, primary_key=True)
    linea = Column(Integer, primary_key=True)
    id_codbarra = Column(Integer, ForeignKey("public.m_artxcodigobarra.id_codbarra"), nullable=False)
    id_lote = Column(Integer, nullable=False)
    id_ubicacion = Column(Integer, nullable=False)
    costo = Column(Numeric(20, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_venta = Column(Numeric(20, 2), nullable=False)

    cabecera = relationship("CargaStock", back_populates="detalles")
    articulo = relationship(
        "CodigosBarra",
        primaryjoin="DetalleCargaStock.id_codbarra == CodigosBarra.id_codbarra",
        foreign_keys=[id_codbarra]
    )
