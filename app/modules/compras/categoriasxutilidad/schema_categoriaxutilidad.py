from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


# --- Esquemas auxiliares (solo lectura, ignorados al guardar) ---
class CategoriaSimple(BaseModel):
    nom_categoria: str = Field(alias="nomCategoria", max_length=50)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SubcategoriaSimple(BaseModel):
    nom_subcategoria: str = Field(alias="nomSubcategoria", max_length=50)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CategoriaXUtilidadBase(BaseModel):
    id_emp: int = Field(alias="idEmp")
    id_categoria: int = Field(alias="idCategoria")
    # None = aplica a toda la categoria (el frontend expone esto como una
    # opcion explicita "Toda la categoria" en el combo, no un campo vacio).
    id_subcategoria: Optional[int] = Field(None, alias="idSubcategoria")
    porc_utilidad: Decimal = Field(alias="porcUtilidad", ge=0)
    activo: bool = Field(True, alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CategoriaXUtilidadCreate(CategoriaXUtilidadBase):
    pass


class CategoriaXUtilidadResponse(CategoriaXUtilidadBase):
    id: int = Field(alias="id")
    categoria: Optional[CategoriaSimple] = None
    subcategoria: Optional[SubcategoriaSimple] = None


# --- Esquema para la grilla (fila de la tabla) ---
class CategoriaXUtilidadPaginacion(BaseModel):
    id: int = Field(alias="id")
    id_categoria: int = Field(alias="idCategoria")
    id_subcategoria: Optional[int] = Field(None, alias="idSubcategoria")
    porc_utilidad: Decimal = Field(alias="porcUtilidad")
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    categoria: Optional[CategoriaSimple] = None
    subcategoria: Optional[SubcategoriaSimple] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedCategoriaXUtilidadResponse(BaseModel):
    content: List[CategoriaXUtilidadPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
