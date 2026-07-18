from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


class MedioPagoSimple(BaseModel):
    tipo: str = Field(alias="tipo", max_length=20)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CajaSimple(BaseModel):
    nom_caja: str = Field(alias="nomCaja", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Detalle agrupado (td_cierreturno) ---
class DetalleCierreTurno(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_cierre: Optional[int] = Field(None, alias="idCierre")
    linea: Optional[int] = Field(None, alias="linea")
    concepto: str = Field(alias="concepto", max_length=15)
    id_mediopago: int = Field(alias="idMediopago")
    signo: int = Field(alias="signo")
    importe_sistema: Decimal = Field(alias="importeSistema")
    valor_usuario: Decimal = Field(alias="valorUsuario")
    # valor_usuario - importe_sistema: positivo = sobrante, negativo = faltante.
    diferencia: Decimal = Field(alias="diferencia")
    mediopago: Optional[MedioPagoSimple] = None  # Solo aplica al leer.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Cabecera (t_cierreturno) ---
class CierreTurnoBase(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_emp: int = Field(alias="idEmp")
    id_turno: int = Field(alias="idTurno")
    fecha_cierre: datetime = Field(alias="fechaCierre")
    observacion: Optional[str] = Field(None, alias="observacion", max_length=250)
    imp_base: Decimal = Field(alias="impBase")
    imp_total: Decimal = Field(alias="impTotal")
    descuadre: bool = Field(alias="descuadre")
    imp_descuadre: Decimal = Field(alias="impDescuadre")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])
    detalles: List[DetalleCierreTurno] = Field(default=[], alias="detalles")
    turno: Optional["TurnoSimple"] = None  # Solo aplica al leer.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TurnoSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=16)
    caja: Optional[CajaSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CierreTurnoCreate(CierreTurnoBase):
    pass


# --- Resumen agrupado de td_abrirturno (preview antes de guardar el cierre) ---
class ResumenCierreLinea(BaseModel):
    concepto: str = Field(alias="concepto")
    id_mediopago: int = Field(alias="idMediopago")
    nombre_mediopago: str = Field(alias="nombreMediopago")
    signo: int = Field(alias="signo")
    importe_sistema: Decimal = Field(alias="importeSistema")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ResumenCierre(BaseModel):
    id_turno: int = Field(alias="idTurno")
    imp_base: Decimal = Field(alias="impBase")
    nom_caja: str = Field(alias="nomCaja")
    lineas: List[ResumenCierreLinea] = Field(default=[])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Paginacion (lista de cierres ya realizados) ---
class CierrePaginacion(BaseModel):
    id_trans: int = Field(alias="IdTrans")
    fecha_cierre: datetime = Field(alias="FechaCierre")
    imp_total: Decimal = Field(alias="ImpTotal")
    descuadre: bool = Field(alias="Descuadre")
    imp_descuadre: Decimal = Field(alias="ImpDescuadre")
    turno: Optional[TurnoSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Detalle de facturas dentro de un concepto/medio de pago (nivel 2 del
# drill-down de cierre - clic en una fila de la grilla principal). ---
class DetalleConceptoLinea(BaseModel):
    fecha: datetime = Field(alias="fecha")
    id_trans: int = Field(alias="idTrans")
    factura: str = Field(alias="factura")
    cliente: str = Field(alias="cliente")
    importe: Decimal = Field(alias="importe")
    # Solo distinto de "importe" cuando la factura se pago con mas de un medio
    # (pago mixto) - el frontend muestra "$X de $Y" unicamente en ese caso.
    importe_total_factura: Decimal = Field(alias="importeTotalFactura")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedCierreResponse(BaseModel):
    content: List[CierrePaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
