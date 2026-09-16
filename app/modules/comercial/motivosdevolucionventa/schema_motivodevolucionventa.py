from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


class MotivoDevolucionVentaBase(BaseModel):
    id_emp: int = Field(alias="idEmp")
    cod_motivo: Optional[str] = Field(alias="codMotivo", max_length=10, default=None)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    devuelve_dinero: bool = Field(alias="devuelveDinero", default=False)
    codigo_dian: Optional[int] = Field(alias="codigoDian", default=None)
    afecta_stock: bool = Field(alias="afectaStock", default=True)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MotivoDevolucionVentaCreate(MotivoDevolucionVentaBase):
    pass


class MotivoDevolucionVentaResponse(MotivoDevolucionVentaBase):
    id: int = Field(alias="idMotivo")


class MotivoDevolucionVentaPaginacion(BaseModel):
    id: int = Field(alias="id")
    cod_motivo: str = Field(alias="motivo", max_length=10)
    nom_motivo: str = Field(alias="nombreMotivo", max_length=80)
    devuelve_dinero: bool = Field(alias="devuelveDinero")
    afecta_stock: bool = Field(alias="afectaStock")
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedMotivoDevolucionVentaResponse(BaseModel):
    content: List[MotivoDevolucionVentaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int


class MotivoDevolucionVentaCombo(BaseModel):
    id: int = Field(alias="idMotivo")
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)
    devuelve_dinero: bool = Field(alias="devuelveDinero")
    afecta_stock: bool = Field(alias="afectaStock")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
