from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


class ConceptoSimple(BaseModel):
    nom_concepto: str = Field(alias="nomConcepto", max_length=100)
    signo: int = Field(alias="signo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MovCajaBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_concepto: int = Field(alias="idConcepto")
    id_turno: int = Field(alias="idTurno")
    fecha: date = Field(alias="fecha")
    observacion: Optional[str] = Field(None, alias="observacion", max_length=250)
    # El signo se resuelve del concepto elegido en el servidor - nunca se confia
    # en lo que mande el cliente (ver repository_movcaja.create_movcaja).
    importe: Decimal = Field(alias="importe", gt=0)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])
    concepto: Optional[ConceptoSimple] = None  # Solo aplica al leer.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MovCajaCreate(MovCajaBase):
    pass


# --- Paginacion ---
class MovCajaPaginacion(BaseModel):
    id: int = Field(alias="Id")
    fecha: date = Field(alias="Fecha")
    importe: Decimal = Field(alias="Importe")
    signo: int = Field(alias="Signo")
    concepto: Optional[ConceptoSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedMovCajaResponse(BaseModel):
    content: List[MovCajaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
