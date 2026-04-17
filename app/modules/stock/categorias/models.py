from sqlalchemy import Boolean, Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Categoria(Base):
    __tablename__ = "m_categorias"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_categoria', name='m_categorias_cod_emp_cod_categoria_key'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, nullable=False)
    cod_categoria = Column(String(15), nullable=False)
    nom_categoria = Column(String(50))
    estado = Column(Boolean, default=True)
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, onupdate=func.now(), nullable=True)
    # Relación para cargar subcategorías automáticamente
    subcategorias = relationship("Subcategoria", back_populates="parent", cascade="all, delete-orphan")
    subcategoriasmodel= relationship("SubcategoriaModel", back_populates="parent", cascade="all, delete-orphan")

class Subcategoria(Base):
    __tablename__ = "m_subcategorias"
    __table_args__ = (
        UniqueConstraint('categoria_id', 'cod_subcategoria', name='m_subcategorias_cod_emp_cod_subcategoria_key'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("public.m_categorias.id"), nullable=False)
    cod_subcategoria = Column(String(20), nullable=False)
    nom_subcategoria = Column(String(50))

    #Propiedad para consultar si la subCategoria tiene algun articulo ya relacionado.
    @property
    def tiene_articulos(self) -> bool:
        return len(self.articulos) > 0

    parent = relationship("Categoria", back_populates="subcategorias")
    articulos = relationship("Articulo", back_populates="subcategoria")

class SubcategoriaModel(Base):
    __tablename__ = "m_subcategoriasmodel"
    __table_args__ = ({'schema': 'public'})

    id = Column(Integer, primary_key=True,nullable=False)
    categoria_id = Column(Integer, ForeignKey("public.m_categorias.id"), nullable=False)
    linea = Column(Integer,primary_key=True,nullable=False)  

    cod_subcategoria = Column(String(20), nullable=False)
    nom_subcategoria = Column(String(50))

    parent = relationship("Categoria", back_populates="subcategoriasmodel")