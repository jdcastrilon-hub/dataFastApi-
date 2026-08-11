from sqlalchemy import Column, Integer, Sequence, String, BigInteger, Date, DateTime, JSON, Numeric, ForeignKey
from sqlalchemy.orm import relationship, foreign
from app.database import Base


class CargaPrecios(Base):
    __tablename__ = "t_cargaprecios"

    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    id_lista = Column(Integer, ForeignKey("m_listaprecio.id_lista"), nullable=False)
    documento = Column(String(10), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    fecha_carga = Column(Date, nullable=False)
    observacion = Column(String(250))
    nombre_archivo = Column(String(150))
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, nullable=False)
    logs = Column(JSON)

    detalles = relationship("DetalleCargaPrecios", back_populates="cabecera", passive_deletes=True)
    lista = relationship("MListaPrecio")


class DetalleCargaPrecios(Base):
    __tablename__ = "td_cargaprecios"

    id_trans = Column(BigInteger, ForeignKey("t_cargaprecios.id_trans"), primary_key=True)
    id_articulo = Column(Integer, primary_key=True)
    linea = Column(Integer, primary_key=True)
    precio_venta = Column(Numeric(20, 2), nullable=False)

    cabecera = relationship("CargaPrecios", back_populates="detalles")
    # Sin FK declarada (mismo criterio ya usado en td_cargastock/p_precios para
    # referencias a m_articulos entre modulos) - viewonly solo para poder
    # mostrar codigo/nombre al ver una carga ya procesada.
    articulo = relationship(
        "Articulo",
        primaryjoin="foreign(DetalleCargaPrecios.id_articulo) == Articulo.id_articulo",
        viewonly=True,
        uselist=False
    )
