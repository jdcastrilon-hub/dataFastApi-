from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class UnidadBase(BaseModel):
    cod_unidad: str = Field(alias="codUnidad", max_length=10)
    nom_unidad: str = Field(alias="nomUnidad", max_length=50)
    es_paquete: str = Field(alias="esPaquete", max_length=2)
    convuni: int = Field(alias="convertUnidad")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para crear (lo que recibe el POST)
class UnidadCreate(UnidadBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class UnidadResponse(UnidadBase):
    id: int

# Esquema para paginacion (fila de la tabla)
class UnidadPaginacion(BaseModel):
    id: int
    cod_unidad: str = Field(alias="codUnidad", max_length=10)
    nom_unidad: str = Field(alias="nomUnidad", max_length=50)
    es_paquete: str = Field(alias="esPaquete", max_length=2)
    convuni: int = Field(alias="convertUnidad")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class PaginatedUnidadResponse(BaseModel):
    content: List[UnidadPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para combos en la pagina Web (usado hoy por articulos-stock vía /list)
class UnidadCombo(BaseModel):
    id: int
    cod_unidad: str = Field(alias="codUnidad", max_length=10)
    nom_unidad: str = Field(alias="nomUnidad", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
