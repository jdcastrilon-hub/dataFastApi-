from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, Numeric, JSON, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Compra(Base):
    __tablename__ = "t_compras"
    __table_args__ = {"schema": "public"}

    # Usamos BigInteger para id_trans y vinculamos la secuencia 'id_transaccion'
    id_trans = Column(BigInteger, Sequence('id_transaccion'), primary_key=True, index=True)
    
    id_emp = Column(Integer, ForeignKey("public.m_empresa.id_emp"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("public.m_proveedores.id_proveedor"), nullable=False)
    
    fec_doc = Column(Date, nullable=False)
    documento = Column(String(16), nullable=False)
    nro_docum = Column(Integer, nullable=False)
    remito = Column(String(30), nullable=False)
    status= Column(String(2), nullable=False)
    ingresa_bodega = Column(String(2), nullable=False)
    id_bodega = Column(Integer,ForeignKey("m_bodegas.id"), nullable=False)
    id_estado = Column(Integer, nullable=False)
    
    # Manejo de precisión decimal para importes
    imp_neto = Column(Numeric(14, 2), nullable=False)
    imp_descuento = Column(Numeric(14, 2), nullable=False)
    imp_total = Column(Numeric(14, 2), nullable=False)
    
    observaciones = Column(String(250), nullable=False)
    
    # Impuestos
    impuesto1 = Column(String(6), nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    impuesto2 = Column(String(6), nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    impuesto3 = Column(String(6), nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)
    
    vista = Column(String(16), nullable=False)
    fecha_mod = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    logs = Column(JSON, nullable=True)

    # Relaciones
    empresa = relationship("Empresa", back_populates="proveedores")
    proveedor = relationship("Proveedor" , back_populates="compras")
    bodega = relationship(
    "Bodega", 
    back_populates="compras",
    primaryjoin="Compra.id_bodega == Bodega.id",
    foreign_keys=[id_bodega]
    )
    # Relación para cargar detalle automáticamente
    detalles = relationship("DetalleCompra", back_populates="parent", cascade="all, delete-orphan")
    nuevoCodigoBarra = relationship("DetalleCompraNuevoCodigoBarra", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Compra(id_trans={self.id_trans}, nro_docum={self.nro_docum}, proveedor={self.id_proveedor})>"
    
class DetalleCompra(Base):
    __tablename__ = "td_compras"
    __table_args__ = {"schema": "public"}

    # Llave Primaria Compuesta
    id_trans = Column(Integer, ForeignKey("public.t_compras.id_trans"), primary_key=True)    
    linea = Column(Integer, primary_key=True)

    id_articulo = Column(Integer, nullable=False) 
    id_codbarra = Column(Integer, ForeignKey("public.m_artxcodigobarra.id_codbarra"), nullable=False)
    ref_compras = Column(String(100), nullable=False)
    
    # Precios y Costos (Numeric para precisión financiera)
    costo_unit = Column(Numeric(14, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    id_lote = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
    porc_dcto = Column(Numeric, nullable=False)
    imp_dcto = Column(Numeric(14, 2), nullable=False)
    
    # Impuesto 1
    impuesto1 = Column(String(6), nullable=False)
    id_tasaimp1 = Column(Integer,ForeignKey("public.m_impuesto.id"), nullable=False)
    valor_impuesto1 = Column(Numeric(14, 2), nullable=False)
    
    # Impuesto 2
    impuesto2 = Column(String(6), nullable=False)
    id_tasaimp2 = Column(Integer, nullable=False)
    valor_impuesto2 = Column(Numeric(14, 2), nullable=False)
    
    # Impuesto 3
    impuesto3 = Column(String(6), nullable=False)
    id_tasaimp3 = Column(Integer, nullable=False)
    valor_impuesto3 = Column(Numeric(14, 2), nullable=False)
     
    # Totales de la línea
    costo_total = Column(Numeric(14, 2), nullable=False)
    importe = Column(Numeric(14, 2), nullable=False)

    parent = relationship("Compra", back_populates="detalles")
    #referencias
    articulo = relationship(
    "CodigosBarra", 
    back_populates="compras",
    primaryjoin="DetalleCompra.id_codbarra == CodigosBarra.id_codbarra",
    foreign_keys=[id_codbarra]
    ) 
    detalleimpuesto1 = relationship("Impuesto", back_populates="compras") 

class DetalleCompraNuevoCodigoBarra(Base):
    __tablename__ = "td_comprasnewcodbarra"
    __table_args__ = {"schema": "public"}

     # Llave Primaria Compuesta
    id_trans = Column(Integer, ForeignKey("public.t_compras.id_trans"), primary_key=True)
    id_articulo = Column(Integer, primary_key=True) # Podría ser FK a m_articulos si la tienes
    id_codbarra= Column(Integer, primary_key=True)
    linea = Column(Integer, primary_key=True)

    cod_barra = Column(String(50), nullable=False)
    ref_barra = Column(String(100), nullable=False)

    parent = relationship("Compra", back_populates="nuevoCodigoBarra")
