from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from app.database import Base


# Tablas puente: opt-in por empresa sobre los catalogos globales
# m_periodicidad / m_formulaprestamo. Presencia de la fila = habilitado
# (patron borrar-e-reinsertar de m_confcomercial, sin columna `activo`).
class PeriodicidadXEmpresa(Base):
    __tablename__ = "m_periodicidadxempresa"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    id_periodicidad = Column(Integer, ForeignKey("public.m_periodicidad.id"), primary_key=True)
    fecha_mod = Column(DateTime, nullable=False, default=func.now())


class FormulaPrestamoXEmpresa(Base):
    __tablename__ = "m_formulaprestamoxempresa"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    id_formula = Column(Integer, ForeignKey("public.m_formulaprestamo.id"), primary_key=True)
    fecha_mod = Column(DateTime, nullable=False, default=func.now())
