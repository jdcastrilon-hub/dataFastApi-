from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, JSON, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class MCaja(Base):
    __tablename__ = "m_cajas"

    id = Column(BigInteger, primary_key=True, index=True)
    id_emp = Column(Integer, primary_key=False, nullable=False)
    id_sucursal_emp = Column(Integer, ForeignKey("public.m_sucursales.id"), nullable=False)
    cod_caja = Column(String(15), primary_key=False, nullable=False)
    nom_caja = Column(String(100), nullable=False)
    cajapos = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
    id_cliente = Column(Integer, primary_key=False, nullable=False)
    id_bodega = Column(Integer, primary_key=False, nullable=False)
    id_estado = Column(Integer, primary_key=False, nullable=False)
    documento = Column(String(10), nullable=False)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    usuarios = relationship("MCajasXUser", back_populates="caja", cascade="all, delete-orphan")
    turnos = relationship("TAbrirTurno", back_populates="caja")
    sucursal = relationship("Sucursal", back_populates="caja") 


class MCajasXUser(Base):
    __tablename__ = "m_cajasxuser"

    id_caja = Column(Integer, ForeignKey("m_cajas.id"), primary_key=True)
    usuario = Column(String(16), primary_key=True, nullable=False)


    caja = relationship("MCaja", back_populates="usuarios")