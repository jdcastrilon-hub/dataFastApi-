from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint
import datetime
from app.database import Base


class MotivoDevolucionVenta(Base):
    __tablename__ = "m_motivodevolucionventa"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_motivo', name='m_motivodevolucionventa_unique'),
        {"schema": "public"}
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    cod_motivo = Column(String(10), nullable=False)
    nom_motivo = Column(String(80), nullable=False)
    # Si esta marcado, la nota que use este motivo exige id_turno/id_caja (igual
    # que factura) y genera un GastoCaja real. Si no, el importe de la nota queda
    # como saldo a favor del cliente (p_saldocliente/s_saldocliente) en vez de
    # salir de caja.
    devuelve_dinero = Column(Boolean, nullable=False, default=False)
    # Referencia al concepto oficial DIAN de nota credito/debito (1-6) - nullable,
    # todavia no se emite factura electronica. Un motivo puede no mapear a un
    # codigo fijo (ej. "Ajuste de Valor" cubre los conceptos 3 y 4 a la vez).
    codigo_dian = Column(Integer, nullable=True)
    # Si la nota con este motivo reingresa mercancia fisica a bodega o es un
    # ajuste puramente de valor (sin movimiento de inventario) - eje
    # independiente de devuelve_dinero (ese decide de donde sale el dinero).
    afecta_stock = Column(Boolean, nullable=False, default=True)
    activo = Column(String(2), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    logs = Column(JSON, nullable=True)
