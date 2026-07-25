from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class UsuarioSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ConceptoXUserBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional[UsuarioSimple] = None  #Solo se completa al leer (join), se ignora al guardar.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class ConceptoBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_emp: int = Field(alias="idEmp")
    nom_concepto: str = Field(alias="nomConcepto", max_length=100)
    signo: int = Field(alias="signo")
    status: bool = Field(alias="status")
    aplica_limit: bool = Field(alias="aplicaLimit")
    imp_limit: Optional[float] = Field(None, alias="impLimit")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]
    usuarios: List[ConceptoXUserBase] = Field(default=[], alias="usuarios")

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class ConceptoCreate(ConceptoBase):
    pass

# Esquema para paginacion
class ConceptoPaginacion(BaseModel):
    id: int
    nom_concepto: str = Field(alias="nomConcepto", max_length=100)
    signo: int = Field(alias="signo")
    status: bool = Field(alias="status")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Combo simple usado por "Movimiento Caja" (comercial) - conceptos activos
# asociados al usuario logueado, filtrados por signo (1=Ingreso/-1=Gasto).
class ConceptoCombo(BaseModel):
    id: int = Field(alias="id")
    nom_concepto: str = Field(alias="nomConcepto", max_length=100)
    signo: int = Field(alias="signo")
    aplica_limit: bool = Field(alias="aplicaLimit")
    imp_limit: Optional[float] = Field(None, alias="impLimit")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedConceptoResponse(BaseModel):
    content: List[ConceptoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
