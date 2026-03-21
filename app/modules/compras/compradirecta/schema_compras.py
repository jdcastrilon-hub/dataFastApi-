from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str    

    # --- Esquemas para la Cabecera ---
class CompraBase(BaseModel):
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_emp : int = Field(alias="idEmp")
    id_proveedor: int = Field(alias="idProveedor")
    fec_doc : datetime = Field(alias="fecDoc")
    documento: str = Field(alias="documento", max_length=10)
    nro_docum: int= Field(alias="nroDocum")
    remito: str = Field(alias="remito", max_length=30)
    ingresa_bodega: str = Field(alias="ingresaBodega", max_length=2)
    id_bodega: int = Field(alias="idBodega")
    id_estado: int= Field(alias="idEstado")
    imp_neto : Decimal= Field(alias="impNeto")
    imp_descuento : Decimal= Field(alias="impDescuento")
    imp_total : Decimal= Field(alias="impTotal")
    observacion: Optional[str] = Field(alias="observaciones", max_length=250)
    impuesto1 : str = Field(alias="impuesto1", max_length=6)
    valor_impuesto1 : Decimal= Field(alias="valorImpuesto1")
    impuesto2 : str = Field(alias="impuesto2", max_length=6)
    valor_impuesto2 : Decimal= Field(alias="valorImpuesto2")
    impuesto3 : str = Field(alias="impuesto3", max_length=6)
    valor_impuesto3 : Decimal= Field(alias="valorImpuesto3")
    vista:  str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    detalles: List[DetalleCompra] = Field(default=[], alias="detalles")
    nuevoCodigoBarra : List[DetalleCompraNuevoCodigoBarra] = Field(default=[], alias="nuevoCodigoBarra")
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)


# --- Esquemas para el Detalle ---
class DetalleCompra(BaseModel):
    #llave compuesta
    id_trans: Optional[int] = Field(None,alias="idTrans")    
    linea: int = Field(alias="linea")
    #campos
    id_articulo: int = Field(alias="idArticulo") 
    id_codbarra: int = Field(alias="idCodBarra") 
    ref_compras:str = Field(alias="refCompras", max_length=100)
    costo_unit: Decimal= Field(alias="costoUnit")
    cantidad: int = Field(alias="cantidad")
    id_lote: int = Field(alias="idLote")
    stock: int = Field(alias="stock")
    impuesto1 : str = Field(alias="impuesto1", max_length=6)
    id_tasaimp1 : int = Field(alias="idTasaimp1")
    valor_impuesto1 : Decimal= Field(alias="valorImpuesto1")
    impuesto2 : str = Field(alias="impuesto2", max_length=6)
    id_tasaimp2 : int = Field(alias="idTasaimp2")
    valor_impuesto2 : Decimal= Field(alias="valorImpuesto2")
    impuesto3 : str = Field(alias="impuesto3", max_length=6)
    id_tasaimp3 : int = Field(alias="idTasaimp3")
    valor_impuesto3 : Decimal= Field(alias="valorImpuesto3")
    costo_total : Decimal= Field(alias="costoTotal")
    importe : Decimal= Field(alias="importeTotal")
    

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

    # --- Esquemas para el Detalle ---
class DetalleCompraNuevoCodigoBarra(BaseModel):
    #llave compuesta
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_articulo: int = Field(alias="idArticulo") 
    id_codbarra: Optional[int] = Field(None,alias="idCodBarra") 
    linea: int = Field(alias="linea")
    #campos
    cod_barra: str = Field(alias="codBarra", max_length=50)
    ref_barra: str = Field(alias="nomBarra", max_length=100)

class CompraCreate(CompraBase):
    pass # id_trans se hereda de la cabecera al insertar

# Esquema para paginacion 
class PaginatedCompraResponse(BaseModel):
    content: List[CompraPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

    # Esquema para paginacion
class CompraPaginacion(BaseModel):
    id_trans : int
    fec_doc: date = Field(alias="Fecha")  
    nro_docum: int = Field(alias="NumOC")  
    remito : str = Field(alias="Remito", max_length=30)
    imp_total : Decimal = Field(alias="Importe")
    proveedor: ProveedorSimple
    bodega : Optional[BodegaSimple] = None

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class ProveedorSimple(BaseModel):
    razon_social: str = Field(alias="nombreCompleto")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)