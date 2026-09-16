from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.database import Base


class FormulaPrestamo(Base):
    """Catalogo GLOBAL de formulas de calculo de cuota. Sin id_emp: un unico
    universo para toda la plataforma. A diferencia de m_periodicidad, `codigo`
    SI es operativo - una funcion futura ramifica sobre ese valor al calcular
    valor_cuota / generar el cronograma. Que formulas ve cada empresa se
    resuelve en m_formulaprestamoxempresa (opt-in por empresa)."""

    __tablename__ = "m_formulaprestamo"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), nullable=False)
    nombre = Column(String(80), nullable=False)
    # Propiedad de la formula, no de la empresa: una misma empresa puede prestar
    # comercialmente Y prestarle a un familiar al 0% sin mora.
    genera_interes_mora = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now())
