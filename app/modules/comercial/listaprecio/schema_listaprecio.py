from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


class ListaPrecioXUserBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional["UsuarioSimple"] = None  # Solo se completa al leer (join); se ignora al guardar.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ListaPrecioBase(BaseModel):
    id_lista: Optional[int] = Field(None, alias="idLista")
    id_emp: int = Field(alias="idEmp")
    nombre: str = Field(alias="nombre", max_length=100)
    id_cliente: Optional[int] = Field(None, alias="idCliente")
    es_general: bool = Field(alias="esGeneral")
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])
    usuarios: List[ListaPrecioXUserBase] = Field(default=[], alias="usuarios")
    cliente: Optional["ClienteSimple"] = None  # Solo aplica para la edicion de la lista.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ListaPrecioCreate(ListaPrecioBase):
    pass


# Esquema para combos en la pagina Web
class ListaPrecioCombo(BaseModel):
    id_lista: int = Field(alias="idLista")
    nombre: str = Field(alias="nombre", max_length=100)
    # Permite que el selector auto-seleccione la general por defecto sin
    # necesitar una segunda llamada.
    es_general: bool = Field(alias="esGeneral")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Esquema para combos que necesitan TODAS las listas activas, no solo las base
# (ej. carga masiva de precios: cualquier lista activa admite carga por archivo).
class ListaPrecioComboTodas(BaseModel):
    id_lista: int = Field(alias="idLista")
    nombre: str = Field(alias="nombre", max_length=100)
    es_general: bool = Field(alias="esGeneral")
    cliente: Optional["ClienteSimple"] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Esquema para paginacion
class ListaPrecioPaginacion(BaseModel):
    id_lista: int = Field(alias="idLista")
    nombre: str = Field(alias="nombre", max_length=100)
    es_general: bool = Field(alias="esGeneral")
    activo: bool = Field(alias="activo")
    cliente: Optional["ClienteSimple"] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedListaPrecioResponse(BaseModel):
    content: List[ListaPrecioPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int


# Esquemas Auxiliares ***********************
class ClienteSimple(BaseModel):
    id_cliente: Optional[int] = Field(None, alias="idCliente")
    cod_tit: str = Field(alias="codTit", max_length=50)
    nom_cliente: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UsuarioSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
# Fin Esquemas Auxiliares ***********************
