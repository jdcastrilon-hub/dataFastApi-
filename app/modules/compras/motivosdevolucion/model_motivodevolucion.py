from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, UniqueConstraint
import datetime
from app.database import Base

class MotivoDevolucion(Base):
    __tablename__ = "m_motivodevolucion"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_motivo', name='m_motivodevolucion_unique'),
        {"schema": "public"}
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    cod_motivo = Column(String(10), nullable=False)
    nom_motivo = Column(String(80), nullable=False)
    activo = Column(String(2), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    logs = Column(JSON, nullable=True)
