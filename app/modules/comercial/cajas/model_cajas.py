from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, JSON, ForeignKeyConstraint
from sqlalchemy.orm import relationship, foreign
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
    # Solo aplica cuando cajapos=true - maximo de horas que un turno puede quedar
    # abierto antes de considerarse vencido (ver TAbrirTurno.fecha_apertura /
    # repository_turno.validar_turnoxusuario). Nullable: sin limite si no se define.
    horas_turno = Column(Integer, nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    usuarios = relationship("MCajasXUser", back_populates="caja", cascade="all, delete-orphan")
    turnos = relationship("TAbrirTurno", back_populates="caja")
    sucursal = relationship("Sucursal", back_populates="caja")

    # id_cliente no tiene FK declarada en la tabla real (igual que otras tablas de
    # este proyecto) - relacion viewonly con join explicito, solo para poder
    # traer el cliente por defecto de la caja en la edicion.
    cliente = relationship(
        "Cliente",
        primaryjoin="MCaja.id_cliente == foreign(Cliente.id_cliente)",
        viewonly=True,
        uselist=False
    )


class MCajasXUser(Base):
    __tablename__ = "m_cajasxuser"

    id = Column(Integer, primary_key=True, index=True)
    id_caja = Column(Integer, ForeignKey("m_cajas.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("public.md_usuarios.id_usuario"), nullable=False)

    caja = relationship("MCaja", back_populates="usuarios")
    usuario = relationship("Usuario")