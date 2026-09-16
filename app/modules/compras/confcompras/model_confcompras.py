from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ConfCompras(Base):
    __tablename__ = "m_confcompras"
    __table_args__ = {"schema": "public"}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    # Estado de mercancia (m_estados) que se asigna por defecto a toda Compra
    # Directa - el usuario deja de elegirlo en el formulario. Nullable: hasta
    # que la empresa no lo configure aca, no hay valor por defecto.
    id_estado_comp = Column(Integer, ForeignKey("public.m_estados.id"), nullable=True)
    # Si la empresa quiere digitar precio de venta/utilidad directo en Compra
    # Directa (a futuro) o si ese proceso lo maneja aparte por lista de
    # precios. Deny by default.
    act_precio_compra = Column(Boolean, nullable=False, default=False)
    # Ultimo nivel de la jerarquia de utilidad (subcategoria -> categoria ->
    # general, ver m_categoriasxutilidad). Nullable: sin configurar, no hay
    # sugerencia de precio de venta (no es lo mismo que "0% de markup").
    porc_utilidad_general = Column(Numeric(5, 2), nullable=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    estado_comp = relationship("Estado")
