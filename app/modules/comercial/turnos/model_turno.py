from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, Date, Boolean, Numeric, String, DateTime, JSON, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class TAbrirTurno(Base):
    __tablename__ = "t_abrirturno"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # Llaves que forman la relación con m_cajas
    id_caja = Column(Integer,ForeignKey("m_cajas.id"), nullable=False)
    
    fec_doc = Column(Date, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    imp_base = Column(Numeric(14, 2), nullable=True)
    usuario = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    caja = relationship("MCaja", back_populates="turnos")


