from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, Date, Boolean, Numeric, String, DateTime, JSON, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class TAbrirTurno(Base):
    __tablename__ = "t_abrirturno"

    id = Column(Integer, primary_key=True, nullable=False)
    
    # Llaves que forman la relación con m_cajas
    id_caja = Column(Integer,ForeignKey("m_cajas.id"), nullable=False)
    
    fec_doc = Column(Date, nullable=True)
    # Se fija UNA sola vez al crear el turno (nunca se toca en update_turno) - es la
    # unica fuente confiable de "cuando se abrio realmente" para calcular si el
    # turno ya vencio (ver m_cajas.horas_turno). fec_doc es solo Date (sin hora) y
    # fecha_mod cambia con cualquier edicion posterior, ninguna de las dos sirve
    # para esto.
    fecha_apertura = Column(DateTime, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    imp_base = Column(Numeric(14, 2), nullable=True)
    usuario = Column(String(16), nullable=False)
    observacion = Column(String(100), nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    caja = relationship("MCaja", back_populates="turnos")

