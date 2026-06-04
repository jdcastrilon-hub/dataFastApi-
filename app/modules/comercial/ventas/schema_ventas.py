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
class VentaBase(BaseModel):
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_emp : int = Field(alias="idEmp")
    id_cliente: int = Field(alias="idCliente")    
    id_sucursal_emp : int = Field(alias="idSucursalEmp")
    fec_doc : datetime = Field(alias="fecDoc")
    documento: str = Field(alias="documento", max_length=16)
    nro_docum: int= Field(alias="nroDocum")
    serie_docum: str = Field(alias="serie", max_length=8)   
    secuencia :  str = Field(alias="secuencia", max_length=20)   
    id_bodega: int = Field(alias="idBodega")
    id_estado: int= Field(alias="idEstado")
    id_pago : int= Field(alias="idPago")
    fec_venc : datetime = Field(alias="fecVenc")
    imp_neto : Decimal= Field(alias="impNeto")
    porc_dcto : Decimal= Field(alias="porcDescuento")
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
    detalles: List[DetalleVenta] = Field(default=[], alias="detalles")
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)


# --- Esquemas para el Detalle ---
class DetalleVenta(BaseModel):
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
    porc_dcto: Decimal = Field(alias="porcDcto")
    imp_dcto : Decimal= Field(alias="importeDcto")
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

class ventaCreate(VentaBase):
    pass # id_trans se hereda de la cabecera al insertar