from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class CajaXUserBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional[UsuarioSimple] = None  #Solo se completa al leer (join), se ignora al guardar.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class CajaBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_emp : int  = Field(alias="idEmp")
    id_sucursal_emp: int = Field(alias="idSucursal")
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)
    cajapos: bool = Field(alias="cajaPos")
    # Solo aplica cuando cajapos=true - maximas horas que un turno de esta caja
    # puede quedar abierto antes de considerarse vencido.
    horas_turno: Optional[int] = Field(None, alias="horasTurno")
    status: bool = Field(alias="status")
    id_cliente : int = Field(alias="idCliente")
    id_bodega : int = Field(alias="idBodega")
    id_estado : int = Field(alias="idEstado")
    documento : str = Field(alias="documento", max_length=10)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]
    usuarios:  List[CajaXUserBase] = Field(default=[], alias="usuarios")
    sucursal: Optional[SucursalSimple] = None  #Solo aplica para la edicion de la caja.
    cliente: Optional[ClienteSimple] = None  #Solo aplica para la edicion de la caja.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class CajaCreate(CajaBase):
    pass


# Esquema para combos en la pagina Web
class CajaCombo(BaseModel):
    id : int = Field(alias="idCaja")
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class PaginatedCajaResponse(BaseModel):
    content: List[CajaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

class CajaPaginacion(BaseModel):
    id: int
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)
    cajapos: bool = Field(alias="cajaPos")
    status: bool = Field(alias="status")
    sucursal: Optional[SucursalSimple] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

#Esquemas Auxiliares***********************
class SucursalSimple(BaseModel):
    nom_sucursal: str = Field(alias="nomSucursal", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ClienteSimple(BaseModel):
    id_cliente: Optional[int] = Field(None, alias="idCliente")
    id_persona: Optional[int] = Field(None, alias="idPersona")
    cod_tit: str = Field(alias="codTit", max_length=50)
    nom_cliente: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UsuarioSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
#Fin Esquemas Auxiliares***********************