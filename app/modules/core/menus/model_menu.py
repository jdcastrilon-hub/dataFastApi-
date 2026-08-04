from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Menu(Base):
    __tablename__ = "md_menu"

    id_menu = Column(Integer, primary_key=True, autoincrement=True)
    id_modulo = Column(Integer, ForeignKey("public.md_modulo.id_modulo"), nullable=False)
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(250), nullable=True)
    ruta = Column(String(250), nullable=True)
    icono = Column(String(100), nullable=True)
    # Auto-referencia: Menu no declara __table_args__ de schema (a diferencia de
    # casi todo lo demas en este codebase), asi que se registra en SQLAlchemy
    # bajo la clave "md_menu" a secas, no "public.md_menu" - por eso esta FK
    # tiene que ser sin el prefijo "public.", o falla al configurar mappers
    # (mismo gotcha ya documentado para MenuPermiso.id_menu).
    id_padre = Column(Integer, ForeignKey("md_menu.id_menu"), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    visible = Column(Boolean, nullable=False, default=True)
    activo = Column(Boolean, nullable=False, default=True)
    es_contenedor = Column(Boolean, nullable=False, default=False)
