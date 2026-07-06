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
    id_padre = Column(Integer, ForeignKey("public.md_menu.id_menu"), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    visible = Column(Boolean, nullable=False, default=True)
    activo = Column(Boolean, nullable=False, default=True)
    es_contenedor = Column(Boolean, nullable=False, default=False)
