from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Articulo(Base):
    __tablename__ = "m_articulos"
    __table_args__ = {'schema': 'public'}

    # Llave primaria y campos básicos
    id_articulo = Column(Integer, primary_key=True, index=True)
    cod_articulo = Column(String(30), nullable=False)
    nom_articulo = Column(String(100), nullable=False)
    
    # Llaves foráneas (Relaciones)
    id_negocio = Column(Integer, ForeignKey("public.m_negocios.id"), nullable=False)
    id_categoria = Column(Integer, nullable=False) # Si no tienes m_categorias.id como FK formal, queda así
    id_subcategoria = Column(Integer, ForeignKey("public.m_subcategorias.id"), nullable=False)
    id_unidad = Column(Integer, ForeignKey("public.m_unidades.id"), nullable=False)
    id_tiposervicio = Column(Integer, ForeignKey("public.m_tiposervicio.id"), nullable=False)
    id_impuesto = Column(Integer, ForeignKey("public.m_impuesto.id"), nullable=True)
    id_ref = Column(Integer, nullable=True)

    # Configuración de Stock
    activo_stock = Column(String(2), nullable=False)
    stock_min = Column(Integer, nullable=True)
    stock_max = Column(Integer, nullable=True)

    # Configuración Comercial y Contable
    activo_comercial = Column(String(2), nullable=False)
    grupo_contable = Column(String(20), nullable=False)
    cta_inventario = Column(String(15), nullable=True)

    # Auditoría
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    logs = Column(JSON, nullable=True)

    #Relaciones FK
    objnegocio = relationship("Negocio", back_populates="articulo")
    subcategoria = relationship("Subcategoria", back_populates="articulos")
    unidad = relationship("Unidad", back_populates="articulos") 
    impuesto = relationship("Impuesto", back_populates="articulos") 
    codigosBarra = relationship("CodigosBarra", back_populates="articulo")


    #ToString
    def __repr__(self):
        return f"<Articulo(nom='{self.nom_articulo}', cod='{self.cod_articulo}')>"
    

class CodigosBarra(Base): 
    __tablename__ = "m_artxcodigobarra"
    __table_args__ = {'schema': 'public'}

    # Definimos los campos que forman la clave primaria compuesta
    id_codbarra = Column(Integer,primary_key=True,index=True)
    id_articulo = Column(Integer,ForeignKey("public.m_articulos.id_articulo"),primary_key=True,nullable=False)    
    
    # Otros campos
    cod_barra = Column(String(50), nullable=True)
    ref_barra = Column(String(100), nullable=True)

    # Referecia para articulo
    articulo = relationship("Articulo", back_populates="codigosBarra")
    # Referencia para compras
    compras = relationship("DetalleCompra", back_populates="articulo")

