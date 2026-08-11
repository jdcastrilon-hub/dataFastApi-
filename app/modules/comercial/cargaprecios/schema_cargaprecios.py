from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


# --- Resultado del procesamiento (validacion y/o guardado) ---
class ErrorFila(BaseModel):
    fila: int
    mensaje: str


class ResumenCarga(BaseModel):
    totalFilas: int
    articulosActualizados: int


class ResultadoCarga(BaseModel):
    status: str  # 'success' | 'error'
    message: str
    errores: List[ErrorFila] = []
    resumen: Optional[ResumenCarga] = None
    idTrans: Optional[int] = None


# --- Esquemas para listar/ver cargas ya procesadas ---
class ListaSimple(BaseModel):
    nombre: str = Field(alias="nombre", max_length=100)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ArticuloSimple(BaseModel):
    cod_articulo: str = Field(alias="codArticulo", max_length=30)
    nom_articulo: str = Field(alias="nomArticulo", max_length=100)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DetalleCargaPreciosBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_articulo: int = Field(alias="idArticulo")
    linea: int = Field(alias="linea")
    precio_venta: float = Field(alias="precioVenta")
    articulo: Optional[ArticuloSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CargaPreciosBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_emp: int = Field(alias="idEmpresa")
    id_lista: int = Field(alias="idLista")
    documento: str = Field(alias="documento", max_length=10)
    nro_docum: int = Field(alias="nroDocum")
    fecha_carga: datetime = Field(alias="fechaCarga")
    observacion: Optional[str] = Field(None, alias="observacion", max_length=250)
    nombre_archivo: Optional[str] = Field(None, alias="nombreArchivo", max_length=150)
    vista: str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    detalles: List[DetalleCargaPreciosBase] = Field(default=[], alias="detalles")
    lista: Optional[ListaSimple] = None
    logs: List[LogEntry] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CargaPreciosPaginacion(BaseModel):
    id_trans: int = Field(alias="idTrans")
    nro_docum: int = Field(alias="nroDocum")
    fecha_carga: datetime = Field(alias="fechaCarga")
    observacion: Optional[str] = Field(None, alias="observacion")
    nombre_archivo: Optional[str] = Field(None, alias="nombreArchivo")
    lista: Optional[ListaSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedCargaPreciosResponse(BaseModel):
    content: List[CargaPreciosPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
