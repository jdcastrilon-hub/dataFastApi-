from sqlalchemy import Column, Integer, Sequence, String, BigInteger, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TrasladoStock(Base):
    __tablename__ = "t_trasladobodega"

    id_trans = Column(BigInteger,Sequence('id_transaccion'), primary_key=True, index=True)
    id_bodega_origen = Column(Integer, nullable=False)
    id_bodega_destino = Column(Integer, nullable=False)
    documento = Column(String(10), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    id_calculo = Column(Integer, nullable=False)
    fecha_movimiento = Column(Date, nullable=False)
    id_estado_origen = Column(Integer, nullable=False)
    id_estado_destino = Column(Integer, nullable=False)
    observacion = Column(String(250))
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, nullable=False)
    logs = Column(JSON)

    # Relación con el detalle
    detalles = relationship("DetalleTrasladoStock", back_populates="cabecera")



class DetalleTrasladoStock(Base):
    __tablename__ = "td_trasladobodega"

    # Definición de Llave Compuesta
    id_trans = Column(BigInteger, ForeignKey("t_trasladobodega.id_trans"), primary_key=True)
    id_articulo = Column(Integer, primary_key=True)
    linea = Column(Integer, primary_key=True)
    
    id_ubicacion = Column(Integer, nullable=False)
    id_lote = Column(Integer, nullable=False)
    cant_disp = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)

    cabecera = relationship("TrasladoStock", back_populates="detalles")