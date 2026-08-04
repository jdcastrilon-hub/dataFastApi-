from pydantic import BaseModel, ConfigDict, Field
from typing import List

# Combo de modulos (sin CRUD propio, solo lectura para el filtro)
class ModuloCombo(BaseModel):
    id_modulo: int = Field(alias="idModulo")
    nombre: str = Field(alias="nombre")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Combo de roles activos de una empresa (para el filtro de la matriz)
class RolCombo(BaseModel):
    id_rol: int = Field(alias="idRol")
    nombre: str = Field(alias="nombre")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AccionMatriz(BaseModel):
    id_menu_permiso: int = Field(alias="idMenuPermiso")
    codigo: str = Field(alias="codigo")
    nombre: str = Field(alias="nombre")
    otorgado: bool = Field(alias="otorgado")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class FormularioMatriz(BaseModel):
    id_menu: int = Field(alias="idMenu")
    nombre: str = Field(alias="nombre")
    acciones: List[AccionMatriz] = Field(default=[], alias="acciones")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class GuardarMatrizRequest(BaseModel):
    id_rol: int = Field(alias="idRol")
    id_modulo: int = Field(alias="idModulo")
    otorgados: List[int] = Field(default=[], alias="otorgados")

    model_config = ConfigDict(populate_by_name=True)

# Habilitacion de modulos por empresa (autoservicio del superadmin) - ver
# docs/tecnica/specs/core/delegacion-permisos-menu-exclusivo.md, Pieza 1.
class ModuloEmpresaResponse(BaseModel):
    id_modulo: int = Field(alias="idModulo")
    nombre: str = Field(alias="nombre")
    activo: bool = Field(alias="activo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ModuloEmpresaUpdate(BaseModel):
    id_modulo: int = Field(alias="idModulo")
    activo: bool = Field(alias="activo")

    model_config = ConfigDict(populate_by_name=True)
