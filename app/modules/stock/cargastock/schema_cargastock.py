from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# --- Resultado del procesamiento (validacion y/o guardado) ---
class ErrorFila(BaseModel):
    fila: int
    mensaje: str

class ArticuloNuevoResumen(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    subcategoria: str

class ResumenCarga(BaseModel):
    totalFilas: int
    articulosNuevos: int
    articulosExistentes: int
    cantidadTotal: int
    articulosNuevosDetalle: List[ArticuloNuevoResumen] = []

class ResultadoCarga(BaseModel):
    status: str  # 'success' | 'error'
    message: str
    errores: List[ErrorFila] = []
    resumen: Optional[ResumenCarga] = None
    idTrans: Optional[int] = None

# --- Esquemas para listar/ver cargas ya procesadas ---
class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class EstadoSimple(BaseModel):
    cod_estado: str = Field(alias="codEstado", max_length=20)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ArticuloSimple(BaseModel):
    cod_barra: str = Field(alias="codArticulo", max_length=50)
    ref_barra: str = Field(alias="nomArticulo", max_length=100)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DetalleCargaStockBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_articulo: int = Field(alias="idArticulo")
    id_codbarra: int = Field(alias="idCodBarra")
    linea: int = Field(alias="linea")
    id_lote: int = Field(alias="idLote")
    id_ubicacion: int = Field(alias="idUbicacion")
    costo: float = Field(alias="costo")
    cantidad: int = Field(alias="cantidad")
    precio_venta: float = Field(alias="precioVenta")
    articulo: Optional[ArticuloSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CargaStockBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_emp: int = Field(alias="idEmpresa")
    id_negocio: int = Field(alias="idNegocio")
    id_bodega: int = Field(alias="idBodega")
    id_estado: int = Field(alias="idEstado")
    id_proveedor: int = Field(alias="idProveedor")
    documento: str = Field(alias="documento", max_length=10)
    nro_docum: int = Field(alias="nroDocum")
    fecha_movimiento: datetime = Field(alias="fechaMovimiento")
    observacion: Optional[str] = Field(None, alias="observacion", max_length=250)
    nombre_archivo: Optional[str] = Field(None, alias="nombreArchivo", max_length=150)
    vista: str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    detalles: List[DetalleCargaStockBase] = Field(default=[], alias="detalles")
    logs: List[LogEntry] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CargaStockPaginacion(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    fecha_movimiento: datetime = Field(alias="fechaMovimiento")
    observacion: Optional[str] = Field(None, alias="Observaciones")
    nombre_archivo: Optional[str] = Field(None, alias="nombreArchivo")
    bodega: Optional[BodegaSimple] = None
    estado: Optional[EstadoSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PaginatedCargaStockResponse(BaseModel):
    content: List[CargaStockPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
