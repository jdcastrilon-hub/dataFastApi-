from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class UsuarioSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BancoXUserBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional[UsuarioSimple] = None  #Solo se completa al leer (join), se ignora al guardar.

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

# Esquema Molde
class BancoBase(BaseModel):
    id_emp: int = Field(alias="idEmpresa")
    cod_banco: Optional[str] = Field(alias="codBanco", max_length=10, default=None)
    nom_banco: str = Field(alias="nomBanco", max_length=100)
    nro_cuenta: str = Field(alias="nroCuenta", max_length=30)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    logs: List[LogEntry]
    usuarios: List[BancoXUserBase] = Field(default=[], alias="usuarios")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion
class BancoPaginacion(BaseModel):
    id: int
    cod_banco: str = Field(alias="codBanco", max_length=10)
    nom_banco: str = Field(alias="nomBanco", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class PaginatedBancoResponse(BaseModel):
    content: List[BancoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para crear (lo que recibe el POST)
class BancoCreate(BancoBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class BancoResponse(BancoBase):
    id: int

# Esquema para combos en la pagina Web (ej. seleccion de banco en Medio de Pago)
class BancoCombo(BaseModel):
    id: int = Field(alias="idBanco")
    cod_banco: str = Field(alias="codBanco", max_length=10)
    nom_banco: str = Field(alias="nomBanco", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
