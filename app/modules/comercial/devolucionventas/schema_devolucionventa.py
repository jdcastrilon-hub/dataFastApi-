from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


# --- Esquemas para la Cabecera ---
class NotaFacturaBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_emp: int = Field(alias="idEmp")
    id_sucursal: int = Field(alias="idSucursal")
    id_cliente: int = Field(alias="idCliente")
    id_trans_ref: int = Field(alias="idTransRef")
    id_bodega: int = Field(alias="idBodega")
    id_estado: int = Field(alias="idEstado")
    # Solo se llenan cuando el motivo elegido tiene devuelve_dinero=true.
    id_turno: Optional[int] = Field(None, alias="idTurno")
    id_caja: Optional[int] = Field(None, alias="idCaja")
    fec_doc: datetime = Field(alias="fecDoc")
    documento: str = Field(alias="documento", max_length=16)
    nro_docum: Optional[int] = Field(None, alias="nroDocum")
    serie_docum: str = Field(alias="serie", max_length=8)
    id_motivo: int = Field(alias="idMotivo")
    observacion: Optional[str] = Field(None, alias="observacion", max_length=250)
    imp_neto: Decimal = Field(alias="impNeto")
    impuesto1: str = Field(alias="impuesto1", max_length=6)
    valor_impuesto1: Decimal = Field(alias="valorImpuesto1")
    impuesto2: str = Field(alias="impuesto2", max_length=6)
    valor_impuesto2: Decimal = Field(alias="valorImpuesto2")
    impuesto3: str = Field(alias="impuesto3", max_length=6)
    valor_impuesto3: Decimal = Field(alias="valorImpuesto3")
    imp_total: Decimal = Field(alias="impTotal")
    vista: str = Field(alias="vista", max_length=16)
    status: Optional[str] = Field(None, alias="status", max_length=2)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    detalles: List["DetalleNotaFactura"] = Field(default=[], alias="detalles")
    logs: List[LogEntry]

    # Solo aplican para la edicion/visualizacion de la nota.
    cliente: Optional["ClienteSimple"] = None
    bodega: Optional["BodegaSimple"] = None
    factura_origen: Optional["FacturaOrigenSimple"] = None
    motivo: Optional["MotivoSimple"] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NotaFacturaCreate(NotaFacturaBase):
    pass


# --- Esquemas para el Detalle ---
class DetalleNotaFactura(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    linea: Optional[int] = Field(None, alias="linea")

    id_articulo: int = Field(alias="idArticulo")
    id_codbarra: int = Field(alias="idCodBarra")
    id_lote: int = Field(alias="idLote")
    cantidad: int = Field(alias="cantidad")
    precio_unit: Decimal = Field(alias="precioUnit")
    impuesto1: str = Field(alias="impuesto1", max_length=6)
    id_tasaimp1: int = Field(alias="idTasaimp1")
    valor_impuesto1: Decimal = Field(alias="valorImpuesto1")
    impuesto2: str = Field(alias="impuesto2", max_length=6)
    id_tasaimp2: int = Field(alias="idTasaimp2")
    valor_impuesto2: Decimal = Field(alias="valorImpuesto2")
    impuesto3: str = Field(alias="impuesto3", max_length=6)
    id_tasaimp3: int = Field(alias="idTasaimp3")
    valor_impuesto3: Decimal = Field(alias="valorImpuesto3")
    imp_neto: Decimal = Field(alias="impNeto")
    imp_total: Decimal = Field(alias="impTotal")

    # Solo aplican para ver/editar: se anotan al leer, no se guardan en td_notafactura.
    cod_lote: Optional[str] = Field("", alias="codLote")
    cantidad_vendida: Optional[int] = Field(0, alias="cantidadVendida")

    articulo: Optional["ArticuloSimple"] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Paginacion ---
class PaginatedNotaFacturaResponse(BaseModel):
    content: List["NotaFacturaPaginacion"]
    totalElements: int
    totalPages: int
    number: int
    size: int


class NotaFacturaPaginacion(BaseModel):
    id_trans: int
    fec_doc: date = Field(alias="Fecha")
    nro_docum: int = Field(alias="NumNota")
    status: str = Field(alias="Status", max_length=2)
    imp_total: Decimal = Field(alias="Importe")
    cliente: "ClienteSimple"
    factura_origen: Optional["FacturaOrigenSimple"] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Esquemas Auxiliares ---
class ClienteSimple(BaseModel):
    nom_cliente: str = Field(alias="nombreCompleto")
    cod_tit: str = Field(alias="codTit")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FacturaOrigenSimple(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    serie_docum: str = Field(alias="serie", max_length=8)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MotivoSimple(BaseModel):
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    devuelve_dinero: bool = Field(alias="devuelveDinero")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ArticuloSimple(BaseModel):
    cod_barra: str = Field(alias="codArticulo", max_length=50)
    ref_barra: str = Field(alias="nomArticulo", max_length=100)
    maneja_lote: bool = Field(False, alias="manejaLote")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Esquemas para el flujo cliente -> factura origen -> lineas a devolver ---

class FacturaOrigenBusqueda(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    serie_docum: str = Field(alias="serie", max_length=8)
    fec_doc: date = Field(alias="fecDoc")
    imp_total: Decimal = Field(alias="impTotal")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Linea de la factura origen anotada con el saldo disponible para devolver.
# A diferencia de compras, NO hay tope de stock fisico: la mercancia entra a
# bodega en vez de salir, asi que el unico tope es cuanto queda sin devolver.
class LineaDisponibleNotaCredito(BaseModel):
    linea: int
    id_articulo: int = Field(alias="idArticulo")
    id_codbarra: int = Field(alias="idCodBarra")
    id_lote: int = Field(alias="idLote")
    cod_lote: str = Field("", alias="codLote")
    cod_articulo: str = Field(alias="codArticulo", max_length=50)
    nom_articulo: str = Field(alias="nomArticulo", max_length=100)
    maneja_lote: bool = Field(False, alias="manejaLote")
    cantidad_vendida: int = Field(alias="cantidadVendida")
    precio_unit: Decimal = Field(alias="precioUnit")
    impuesto1: str = Field("", alias="impuesto1", max_length=6)
    id_tasaimp1: int = Field(0, alias="idTasaimp1")
    porc_tasa1: Decimal = Field(Decimal("0"), alias="porcTasa1")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
