from datetime import datetime
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Boolean, Numeric, Sequence, String, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class TCierreTurno(Base):
    __tablename__ = "t_cierreturno"

    # "id_trans" (no "id") a proposito: se reutiliza como p_movimientocajas.id_trans
    # en sp_comercial_cierreturno, asi que DEBE salir del mismo pool compartido que
    # usan todas las demas tablas transaccionales (t_compras/t_ajustestock/
    # t_trasladobodega/etc.) - una secuencia propia puede repetir numeros ya usados
    # por otro documento y romper la llave compuesta (id_trans, linea) de
    # p_movimientocajas. El nombre de columna coincide con el mismo patron que usan
    # esas tablas hermanas.
    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, nullable=False)
    id_emp = Column(Integer, nullable=False)
    id_turno = Column(Integer, ForeignKey("t_abrirturno.id"), nullable=False, unique=True)
    fecha_cierre = Column(DateTime, nullable=False)
    observacion = Column(String(250), nullable=True)
    # Snapshot del saldo de apertura (t_abrirturno.imp_base) - solo de referencia,
    # no se suma a imp_total (ver project_data_comercial_module).
    imp_base = Column(Numeric(14, 2), nullable=False, default=0)
    # Total vendido en el turno (suma de detalles.importe_sistema), sin incluir imp_base.
    imp_total = Column(Numeric(14, 2), nullable=False, default=0)
    descuadre = Column(Boolean, nullable=False, default=False)
    imp_descuadre = Column(Numeric(14, 2), nullable=False, default=0)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    turno = relationship("TAbrirTurno")
    detalles = relationship(
        "TDCierreTurno",
        back_populates="cierre",
        cascade="all, delete-orphan"
    )


class TDCierreTurno(Base):
    __tablename__ = "td_cierreturno"

    id = Column(Integer, primary_key=True, nullable=False)
    id_cierre = Column(BigInteger, ForeignKey("t_cierreturno.id_trans"), nullable=False)
    # Solo de referencia (numero de linea dentro del cierre) - no forma parte de
    # ninguna llave ni constraint, "id" ya es el identificador real de la fila.
    linea = Column(Integer, nullable=True)
    concepto = Column(String(15), nullable=False)
    id_mediopago = Column(Integer, ForeignKey("public.m_mediopagos.id"), nullable=False)
    signo = Column(Integer, nullable=False)
    importe_sistema = Column(Numeric(14, 2), nullable=False, default=0)
    valor_usuario = Column(Numeric(14, 2), nullable=False, default=0)
    diferencia = Column(Numeric(14, 2), nullable=False, default=0)

    cierre = relationship("TCierreTurno", back_populates="detalles")
    mediopago = relationship("MedioPago")
