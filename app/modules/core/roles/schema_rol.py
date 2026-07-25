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

class RolXUsuarioBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional[UsuarioSimple] = None  # Solo se completa al leer (join), se ignora al guardar.

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class RolBase(BaseModel):
    id_rol: Optional[int] = Field(None, alias="idRol")
    id_emp: int = Field(alias="idEmp")
    codigo: str = Field(alias="codigo", max_length=50)
    nombre: str = Field(alias="nombre", max_length=100)
    descripcion: Optional[str] = Field(None, alias="descripcion", max_length=250)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry]
    usuarios: List[RolXUsuarioBase] = Field(default=[], alias="usuarios")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class RolCreate(RolBase):
    pass

# Esquema para paginacion (lista de la pestaña Roles de Administracion)
class RolPaginacion(BaseModel):
    id_rol: int = Field(alias="idRol")
    codigo: str = Field(alias="codigo", max_length=50)
    nombre: str = Field(alias="nombre", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class PaginatedRolResponse(BaseModel):
    content: List[RolPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
