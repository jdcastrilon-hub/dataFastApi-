from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
import datetime
from app.database import Base

class MotivoDevolucion(Base):
    __tablename__ = "m_motivodevolucion"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    cod_motivo = Column(String(10), unique=True, nullable=False)
    nom_motivo = Column(String(80), nullable=False)
    activo = Column(String(2), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    logs = Column(JSON, nullable=True)
