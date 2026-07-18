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
    # Optional: solo se usa de forma transitoria en /save para resolver el codigo
    # de md_numeradores (ver controller_ventas.py) - no se persiste en t_facturas
    # (igual que en compras, que ni siquiera tiene este campo), asi que al releer
    # una venta ya guardada este atributo no existe en el objeto ORM.
    secuencia: Optional[str] = Field(None, alias="secuencia", max_length=20)
    id_bodega: int = Field(alias="idBodega")
    id_estado: int= Field(alias="idEstado")
    # Optional: solo aplica cuando hay turno/caja POS abierto al momento de vender.
    # Si no hay turno abierto, la venta queda sin turno y usa id_caja en su lugar.
    id_turno: Optional[int] = Field(None, alias="idTurno")
    # Optional: solo se usa cuando NO hay turno abierto - caja elegida manualmente
    # entre las asociadas al usuario (m_cajasxuser).
    id_caja: Optional[int] = Field(None, alias="idCaja")
    imp_ingreso: Decimal= Field(alias="impIgreso")
    imp_vuelto: Decimal= Field(alias="impVuelto")
    fec_venc : datetime = Field(alias="fecVenc")
    imp_neto : Decimal= Field(alias="impNeto")
    # Optional: nunca estuvo en este schema pese a que la columna real ya existia -
    # se descartaba en silencio al llegar (ver models_ventas.Factura.tipo_dcto).
    tipo_dcto: Optional[str] = Field(None, alias="tipoDcto", max_length=10)
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
    # Reemplaza a las viejas forma_pago/id_pago de cabecera - permite mas de un
    # medio de pago por venta (ej. Efectivo + Transferencia). Se valida en el
    # repositorio que la suma de importes coincida con imp_total.
    detalles_pago: List[DetallePago] = Field(default=[], alias="detallesPago")
    logs: List[LogEntry]
    cliente: Optional[ClienteSimple] = None  #Solo aplica para la edicion de la venta.
    bodega: Optional[BodegaSimple] = None  #Solo aplica para la edicion de la venta.

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
    # Optional: filas historicas guardadas antes de que se agregara esta columna
    # a td_facturas no tienen este dato (ver models_ventas.FacturaDetalle).
    referencia: Optional[str] = Field(None, alias="referencia", max_length=100)
    precio_unit : Decimal= Field(alias="precio")
    cantidad: int = Field(alias="cantidad")
    stock: int = Field(alias="stock")
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
    imp_neto : Decimal= Field(alias="neto")
    imp_total : Decimal= Field(alias="importeTotal")

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)


# --- Esquemas para las lineas de pago (mismo patron que td_cierreturno) ---
class MedioPagoSimple(BaseModel):
    tipo: str = Field(alias="tipo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DetallePago(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_mediopago: int = Field(alias="idMediopago")
    importe: Decimal = Field(alias="importe")
    mediopago: Optional[MedioPagoSimple] = None  # Solo lectura, para mostrar el tipo al editar/ver.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class ventaCreate(VentaBase):
    pass # id_trans se hereda de la cabecera al insertar

# Esquema para paginacion
class PaginatedVentaResponse(BaseModel):
    content: List[VentaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

class VentaPaginacion(BaseModel):
    id_trans: int
    fec_doc: date = Field(alias="Fecha")
    nro_docum: int = Field(alias="NumDocum")
    documento: str = Field(alias="Documento", max_length=16)
    imp_total: Decimal = Field(alias="Importe")
    cliente: ClienteSimple
    bodega: Optional[BodegaSimple] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

#Esquemas Auxiliares***********************
class ClienteSimple(BaseModel):
    nom_cliente: str = Field(alias="nombreCompleto")
    cod_tit: str = Field(alias="codTit")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#Fin Esquemas Auxiliares***********************