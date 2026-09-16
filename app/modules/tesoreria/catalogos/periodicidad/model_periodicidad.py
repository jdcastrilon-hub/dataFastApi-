from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.database import Base


class Periodicidad(Base):
    """Catalogo GLOBAL de periodicidades de cuota (Diaria/Semanal/.../Bimestral).
    Sin id_emp: es un unico universo para toda la plataforma, se mantiene a
    nivel plataforma (migracion / endpoint Postman). Que periodicidades ve cada
    empresa se resuelve en m_periodicidadxempresa (opt-in por empresa)."""

    __tablename__ = "m_periodicidad"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    # Unico dato operativo: el calculo de fec_venc del cronograma depende de dias.
    dias = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    observacion = Column(String(250), nullable=True)
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now())
