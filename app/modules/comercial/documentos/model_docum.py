from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, foreign
from app.database import Base
import datetime

class DocumentoVenta(Base):
    __tablename__ = "m_documventas"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, primary_key=True, nullable=False)
    id_sucursal_emp = Column(Integer, primary_key=True, nullable=False)
    documento = Column(String(16), primary_key=True, nullable=False)
    descripcion = Column(String(50), nullable=False)
    serie_docum = Column(String(8), nullable=False)
    clase_docum = Column(String(50), nullable=False)
    secuencia = Column(String(50), nullable=False)
    aplica_pos = Column(String(2), nullable=False)
    activo = Column(String(2), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    # id_sucursal_emp no tiene FK declarada en la tabla real (mismo patron que otras
    # tablas de este proyecto) - relacion viewonly con join explicito, solo para
    # poder mostrar el nombre de la sucursal en la lista/edicion.
    sucursal = relationship(
        "Sucursal",
        primaryjoin="DocumentoVenta.id_sucursal_emp == foreign(Sucursal.id)",
        viewonly=True,
        uselist=False
    )