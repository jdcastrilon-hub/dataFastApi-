from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class EstadoBase(BaseModel):
    id_emp: int = Field(alias="idEmpresa")
    cod_estado: str = Field(alias="codEstado", max_length=20)
    nom_estado: str = Field(alias="nomEstado", max_length=80)
    activo: bool = Field(alias="activo")
    obervacion: str = Field(alias="observacion", max_length=250)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class EstadoPaginacion(BaseModel):
    id: int
    cod_estado: str = Field(alias="codEstado", max_length=20)
    nom_estado: str = Field(alias="nomEstado", max_length=80)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class PaginatedEstadoResponse(BaseModel):
    content: List[EstadoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para combos en la pagina Web
class EstadoCombo(BaseModel):
    id: int = Field(alias="id")
    cod_estado: str = Field(alias="codEstado", max_length=10)
    nom_estado: str = Field(alias="nomEstado", max_length=80)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para crear (lo que recibe el POST)
class EstadoCreate(EstadoBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class EstadoResponse(EstadoBase):
    id: int
