from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class TMovCaja(Base):
    __tablename__ = "t_movcajas"

    id = Column(Integer, primary_key=True, index=True)
    # m_conceptoscaja/m_conceptoscajaxuser ya tienen su propio modelo en
    # app.modules.tesoreria.conceptos.model_conceptos (modulo "Tesoreria",
    # CRUD completo ya existente) - no se redefinen aca, solo se referencian
    # por nombre de clase para la relacion.
    id_concepto = Column(Integer, ForeignKey("m_conceptoscaja.id"), nullable=False)
    id_turno = Column(Integer, ForeignKey("t_abrirturno.id"), nullable=False)
    fecha = Column(Date, nullable=True)
    observacion = Column(String(250), nullable=True)
    importe = Column(Numeric(14, 2), nullable=True)
    # Copiado del concepto elegido al momento de crear (no editable directamente
    # por el usuario) - 1 = ingreso, -1 = gasto.
    signo = Column(Integer, nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    concepto = relationship("MConceptoCaja")
    turno = relationship("TAbrirTurno")
