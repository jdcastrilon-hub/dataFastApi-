from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Optional
from app.modules.stock.bodegas import schema_bodega


# Modelo principal de respuesta del Monitor
class MonitorInventario(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    # Usamos Any o dict para que 'detalles' acepte cualquier estructura de tabla
    detalles: List[StockDisponible] 

    class Config:
        from_attributes = True   

# Modelo para cada tarjeta individual de KPI
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str 

class StockDisponible(BaseModel):
    negocio: str = Field(alias="negocio")
    bodega: str = Field(alias="bodega")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    estado: str = Field(alias="estado")
    unidad: str = Field(alias="unidad")
    cantidad: float = Field(alias="cantidad")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

#Filtros
class filtrosgeneralesxempresa(BaseModel):
    idEmpresa: int 
    listnegocio :  List[NegogocioSchema] = []
    listsucursales :  List[SucursalSchema] = []
    listCategorias: List[CategoriaSchema] = []
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

class SucursalSchema(BaseModel):
    id: int = Field(alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    list_bodegas: List[schema_bodega.BodegaCombo] = Field(
        alias="list_bodegas", 
        validation_alias="bodegas" 
    )

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )