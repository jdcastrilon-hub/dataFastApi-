from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime

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
