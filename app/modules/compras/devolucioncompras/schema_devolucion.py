from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# --- Esquemas para la Cabecera ---
class DevolucionCompraBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_emp: int = Field(alias="idEmp")
    id_sucursal: int = Field(alias="idSucursal")
    id_proveedor: int = Field(alias="idProveedor")
    id_compra_origen: int = Field(alias="idCompraOrigen")
    id_bodega: int = Field(alias="idBodega")
    id_estado: int = Field(alias="idEstado")
    fec_doc: datetime = Field(alias="fecDoc")
    documento: str = Field(alias="documento", max_length=16)
    nro_docum: Optional[int] = Field(None, alias="nroDocum")
    id_motivo: int = Field(alias="idMotivo")
    observacion: str = Field(alias="observacion", max_length=250)
    status: Optional[str] = Field(None, alias="status", max_length=2)
    imp_total: Decimal = Field(alias="impTotal")
    vista: str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    detalles: List["DetalleDevolucionCompra"] = Field(default=[], alias="detalles")
    logs: List[LogEntry]

    # Solo aplican para la edicion/visualizacion de la devolucion.
    proveedor: Optional["ProveedorSimple"] = None
    bodega: Optional["BodegaSimple"] = None
    compra_origen: Optional["CompraOrigenSimple"] = None
    motivo: Optional["MotivoSimple"] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)


class DevolucionCompraCreate(DevolucionCompraBase):
    pass


# --- Esquemas para el Detalle ---
class DetalleDevolucionCompra(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    linea: Optional[int] = Field(None, alias="linea")

    id_articulo: int = Field(alias="idArticulo")
    id_codbarra: int = Field(alias="idCodBarra")
    id_lote: int = Field(alias="idLote")
    cantidad: int = Field(alias="cantidad")
    costo_unit: Decimal = Field(alias="costoUnit")
    costo_total: Decimal = Field(alias="costoTotal")

    # Solo aplican para ver/editar: se anotan en get_devolucion_by_id a partir de
    # m_lotes/td_compras (no se guardan en td_devolucioncompras, se recalculan al leer).
    cod_lote: Optional[str] = Field("", alias="codLote")
    cantidad_comprada: Optional[int] = Field(0, alias="cantidadComprada")

    articulo: Optional["ArticuloSimple"] = None  # Solo aplica para ver/editar

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)


# Esquema para paginacion
class PaginatedDevolucionCompraResponse(BaseModel):
    content: List["DevolucionCompraPaginacion"]
    totalElements: int
    totalPages: int
    number: int
    size: int


class DevolucionCompraPaginacion(BaseModel):
    id_trans: int
    fec_doc: date = Field(alias="Fecha")
    nro_docum: int = Field(alias="NumDevolucion")
    status: str = Field(alias="Status", max_length=2)
    imp_total: Decimal = Field(alias="Importe")
    proveedor: "ProveedorSimple"
    compra_origen: Optional["CompraOrigenSimple"] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)


#Esquemas Auxiliares***********************
class ProveedorSimple(BaseModel):
    razon_social: str = Field(alias="nombreCompleto")
    cod_tit: str = Field(alias="codTit")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CompraOrigenSimple(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    remito: str = Field(alias="remito", max_length=30)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MotivoSimple(BaseModel):
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ArticuloSimple(BaseModel):
    cod_barra: str = Field(alias="codArticulo", max_length=50)
    ref_barra: str = Field(alias="nomArticulo", max_length=100)
    maneja_lote: bool = Field(False, alias="manejaLote")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#Fin Esquemas Auxiliares***********************

# --- Esquemas para el flujo proveedor -> compra origen -> lineas a devolver ---

# Combo de compras Finalizadas de un proveedor, para elegir la "compra origen"
class CompraOrigenBusqueda(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    remito: str = Field(alias="remito", max_length=30)
    fec_doc: date = Field(alias="fecDoc")
    imp_total: Decimal = Field(alias="impTotal")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Linea de la compra origen, anotada con el stock disponible ACTUAL (no el
# historico de la compra) - lo que alimenta la modal de seleccion de articulos.
class LineaDisponibleDevolucion(BaseModel):
    linea: int
    id_articulo: int = Field(alias="idArticulo")
    id_codbarra: int = Field(alias="idCodBarra")
    id_lote: int = Field(alias="idLote")
    cod_lote: str = Field("", alias="codLote")
    cod_articulo: str = Field(alias="codArticulo", max_length=50)
    nom_articulo: str = Field(alias="nomArticulo", max_length=100)
    maneja_lote: bool = Field(False, alias="manejaLote")
    cantidad_comprada: int = Field(alias="cantidadComprada")
    costo_unit: Decimal = Field(alias="costoUnit")
    stock_disponible: int = Field(alias="stockDisponible")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
