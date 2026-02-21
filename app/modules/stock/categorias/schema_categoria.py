from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Schema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema para paginacion
class CategoriaPaginacion(BaseModel):
    id : int
    cod_categoria: str = Field(alias="categoria", max_length=20)
    nom_categoria: str = Field(alias="nomCategoria", max_length=80)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

# Esquema para paginacion 
class PaginatedBodegaResponse(BaseModel):
    content: List[CategoriaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

#Schema base de categorias , se tiene la lista de subcategorias
class CategoriaBase(BaseModel):
    id: Optional[int] = Field(alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_categoria: str = Field(alias="codCategoria", max_length=15)
    nom_categoria: str = Field(alias="nomCategoria", max_length=50)
    estado: str = Field(alias="estado", max_length=20)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    subcategorias: List[SubcategoriaBase] = Field(default=[], alias="subCategorias")
    logs: List[LogEntry]
    
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class SubcategoriaBase(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_subcategoria:  str = Field(alias="codSubCategoria", max_length=20)
    nom_subcategoria:  str = Field(alias="nomSubCategoria", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

# Esquema para crear (lo que recibe el POST)
class CategoriaCreate(CategoriaBase):
    pass