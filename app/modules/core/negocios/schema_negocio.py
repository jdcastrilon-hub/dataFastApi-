from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class NegocioBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_negocio: str = Field(alias="codNegocio", max_length=10)
    nom_negocio: str = Field(alias="nomNegocio", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class NegocioCreate(NegocioBase):
    pass

# Esquema para paginacion (lista de la pestaña Negocios de Administracion)
class NegocioPaginacion(BaseModel):
    id: int = Field(alias="id")
    cod_negocio: str = Field(alias="codNegocio", max_length=10)
    nom_negocio: str = Field(alias="nomNegocio", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class PaginatedNegocioResponse(BaseModel):
    content: List[NegocioPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

#Interfaz (NegocioxCategoriasDTO)------------------------------

class NegocioxCategoriasDTO(BaseModel):
    idEmpresa: int 
    nombreEmpresa: str # Mapea a nom_negocio
    listnegocio :  List[NegogocioSchema] = []
    listCategorias: List[CategoriaSchema] = []
    tipoproductos : List[TipoProductoSchema] = []
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class NegogocioSchema(BaseModel):
    id: Optional[int] = Field(alias="idNegocio")
    cod_negocio: str = Field(alias="CodNegocio", max_length=10)
    nom_negocio: str = Field(alias="NomNegocio", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class CategoriaSchema(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_categoria: str = Field(alias="codCategoria", max_length=20)
    nom_categoria: str = Field(alias="nomCategoria", max_length=20)
    subcategorias: List[SubcategoriaSchema] =  Field(default=[], alias="subCategorias")

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class SubcategoriaSchema(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_subcategoria:  str = Field(alias="codSubCategoria", max_length=20)
    nom_subcategoria:  str = Field(alias="nomSubCategoria", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )
    
class TipoProductoSchema(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_servicio: str = Field(alias="codServicio", max_length=20)
    nom_servicio: str = Field(alias="nomServicio", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )
#Interfaz (NegocioxCategoriasDTO)------------------------------


class NegocioCombo(BaseModel):
    id: Optional[int] = Field(alias="idNegocio")
    cod_negocio:  str = Field(alias="Codnegocio", max_length=20)
    nom_negocio: str = Field(alias="NomNegocio", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )
