from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

# md_modulo no tiene CRUD propio (solo se administra directo en Postgres) - este
# modelo existe unicamente para poder consultarlo como combo de filtro.
class Modulo(Base):
    __tablename__ = "md_modulo"
    __table_args__ = {"schema": "public"}

    id_modulo = Column(Integer, primary_key=True)
    codigo = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(250), nullable=True)
    icono = Column(String(100), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)


class Permiso(Base):
    __tablename__ = "md_permisos"
    __table_args__ = {"schema": "public"}

    id_permiso = Column(Integer, primary_key=True)
    codigo = Column(String(20), nullable=False, unique=True)
    nombre = Column(String(50), nullable=False)


class MenuPermiso(Base):
    __tablename__ = "md_menu_permisos"
    __table_args__ = {"schema": "public"}

    id_menu_permiso = Column(Integer, primary_key=True)
    # Menu (model_menu.py) declara __tablename__ = "md_menu" SIN __table_args__ de
    # schema, a diferencia de casi todos los demas modelos - por eso la referencia
    # aqui es "md_menu.id_menu" (sin "public."), o SQLAlchemy no logra resolver el
    # join de la relationship (dos claves de tabla distintas para el mismo md_menu).
    id_menu = Column(Integer, ForeignKey("md_menu.id_menu"), nullable=False)
    id_permiso = Column(Integer, ForeignKey("public.md_permisos.id_permiso"), nullable=False)

    menu = relationship("Menu")
    permiso = relationship("Permiso")


class RolPermiso(Base):
    __tablename__ = "md_rol_permiso"
    __table_args__ = {"schema": "public"}

    # Deny-by-default: la sola existencia de la fila (id_rol, id_menu_permiso)
    # significa "otorgado". No hay columna 'permitido' aqui (esa logica de
    # override en ambos sentidos es propia de md_usuario_permiso, no de esta tabla).
    id_rol = Column(Integer, ForeignKey("public.md_rol.id_rol"), primary_key=True)
    id_menu_permiso = Column(Integer, ForeignKey("public.md_menu_permisos.id_menu_permiso"), primary_key=True)
