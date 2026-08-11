from sqlalchemy import BigInteger, Column, Integer, Sequence, String, Numeric, Date, DateTime, JSON
from app.database import Base


class AjustePrecioLista(Base):
    __tablename__ = 't_ajusteprecio_lista'
    __table_args__ = {'schema': 'public'}

    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)
    linea = Column(Integer, nullable=False)
    id_emp = Column(Integer, nullable=False)
    id_lista = Column(Integer, nullable=False)
    documento = Column(String(15), nullable=False)
    nro_docum = Column(Integer, Sequence('t_ajusteprecio_lista_nro_docum_seq'), nullable=False)
    fec_doc = Column(Date, nullable=False)
    id_articulo = Column(Integer, nullable=False)
    observaciones = Column(String(250), nullable=True)
    imp_precio_actual = Column(Numeric(20, 2), nullable=False)
    imp_precio_nuevo = Column(Numeric(20, 2), nullable=False)
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, nullable=False)
    logs = Column(JSON, nullable=True)
