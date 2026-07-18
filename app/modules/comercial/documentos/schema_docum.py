from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema base con campos comunes
class MDocumVentasBase(BaseModel):
    id_emp: int = Field(alias="idEmpresa")
    id_sucursal_emp: int = Field(alias="idSucursal")
    documento: str = Field(alias="documento", max_length=16)
    descripcion: str = Field(alias="descripcion", max_length=50)
    serie_docum: str = Field(alias="serie", max_length=8)
    clase_docum: str = Field(alias="clase", max_length=50)
    secuencia: str = Field(alias="secuencia", max_length=50)
    aplica_pos: str = Field(alias="aplicaPos", max_length=2)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    # Optional: filas preexistentes en m_documventas pueden tener logs=NULL
    # (mismo caso que se encontro y arreglo en m_mediopagos).
    logs: Optional[List[LogEntry]] = Field(default=None, alias="logs")
    sucursal: Optional[SucursalSimple] = None  #Solo aplica para la edicion/lista.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

# Esquema para crear (puedes omitir la fecha si la genera la DB)
class MDocumVentasCreate(MDocumVentasBase):
    pass

class DocumentCombo(BaseModel):
    documento: str = Field(alias="documento", max_length=16)
    descripcion: str = Field(alias="descripcion", max_length=50)
    serie_docum: str = Field(alias="serie", max_length=8)
    secuencia: str = Field(alias="secuencia", max_length=50)

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

# Esquema para paginacion
class PaginatedDocumVentasResponse(BaseModel):
    content: List[DocumVentasPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

class DocumVentasPaginacion(BaseModel):
    id_sucursal_emp: int = Field(alias="idSucursal")
    documento: str = Field(alias="documento", max_length=16)
    descripcion: str = Field(alias="descripcion", max_length=50)
    serie_docum: str = Field(alias="serie", max_length=8)
    clase_docum: str = Field(alias="clase", max_length=50)
    aplica_pos: str = Field(alias="aplicaPos", max_length=2)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    sucursal: Optional[SucursalSimple] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

#Esquemas Auxiliares***********************
class SucursalSimple(BaseModel):
    nom_sucursal: str = Field(alias="nomSucursal", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#Fin Esquemas Auxiliares***********************