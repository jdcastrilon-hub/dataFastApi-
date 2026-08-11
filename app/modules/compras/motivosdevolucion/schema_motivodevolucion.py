from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class MotivoDevolucionBase(BaseModel):
    id_emp: int = Field(alias="idEmp")
    cod_motivo: Optional[str] = Field(alias="codMotivo", max_length=10, default=None)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para crear (lo que recibe el POST)
class MotivoDevolucionCreate(MotivoDevolucionBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class MotivoDevolucionResponse(MotivoDevolucionBase):
    id: int = Field(alias="idMotivo")

# Esquema para paginacion (fila de la tabla)
class MotivoDevolucionPaginacion(BaseModel):
    id: int = Field(alias="id")
    cod_motivo: str = Field(alias="motivo", max_length=10)
    nom_motivo: str = Field(alias="nombreMotivo", max_length=80)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class PaginatedMotivoDevolucionResponse(BaseModel):
    content: List[MotivoDevolucionPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para combos en la pagina Web
class MotivoDevolucionCombo(BaseModel):
    id: int = Field(alias="idMotivo")
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
