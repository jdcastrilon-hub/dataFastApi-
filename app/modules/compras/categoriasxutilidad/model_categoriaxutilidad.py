from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class CategoriaXUtilidad(Base):
    __tablename__ = "m_categoriasxutilidad"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("public.m_categorias.id"), nullable=False)
    # NULL = la fila aplica a TODA la categoria; con valor = excepcion para
    # esa subcategoria puntual (pisa el % de la categoria completa).
    id_subcategoria = Column(Integer, ForeignKey("public.m_subcategorias.id"), nullable=True)
    porc_utilidad = Column(Numeric(5, 2), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_mod = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(JSON, nullable=True)

    categoria = relationship("Categoria")
    subcategoria = relationship("Subcategoria")
