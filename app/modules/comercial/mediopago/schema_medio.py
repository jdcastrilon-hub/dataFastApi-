from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class MedioPagoBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_emp: int = Field(alias="idEmp")
    tipo: str = Field(alias="tipo", max_length=20)
    orden: Optional[int] = Field(None, alias="orden")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    # Optional porque hay filas preexistentes en m_mediopagos con logs=NULL (creadas
    # antes de que este CRUD existiera) - una lista requerida rompe el GET /search
    # de esas filas con un error de validacion.
    logs: Optional[List[LogEntry]] = Field(default=None, alias="logs")

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class MedioPagoCreate(MedioPagoBase):
    pass

# Esquema para combos en la pagina Web (usado por el combo embebido en sucursal, sin filtrar)
class MedioPagoCombo(BaseModel):
    id: int = Field(alias="id")
    tipo: str = Field(alias="tipo", max_length=20)

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

# Esquema para paginacion
class PaginatedMedioPagoResponse(BaseModel):
    content: List[MedioPagoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

class MedioPagoPaginacion(BaseModel):
    id: int
    tipo: str = Field(alias="tipo", max_length=20)
    orden: Optional[int] = Field(None, alias="orden")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
