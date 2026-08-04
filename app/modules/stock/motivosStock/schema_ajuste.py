from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class MotivoAjusteBase(BaseModel):
    id_emp: int = Field(alias="idEmp")
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    signo: int = Field(alias="signo")
    activo: str = Field(alias="activo", max_length=2)
    cta_inventario: str = Field(alias="ctaInventario", max_length=15)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para crear (lo que recibe el POST)
class MotivoAjusteCreate(MotivoAjusteBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class MotivoAjusteResponse(MotivoAjusteBase):
    id: int = Field(alias="idMotivo")

# Esquema para paginacion (fila de la tabla)
class MotivoAjustePaginacion(BaseModel):
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
class PaginatedMotivoAjusteResponse(BaseModel):
    content: List[MotivoAjustePaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para combos en la pagina Web
class MotivoCombo(BaseModel):
    id: int = Field(alias="idMotivo")
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    # El frontend lo necesita para saber si el motivo resta stock (-1) sin otra consulta
    signo: int = Field(alias="signo")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
