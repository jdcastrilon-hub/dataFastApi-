from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Optional
from app.modules.stock.bodegas import schema_bodega


# Modelo para cada tarjeta individual de KPI
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str

class Comprasrealizadas(BaseModel):
    id_trans : int
    fec_doc: date = Field(alias="fecha")  
    nro_docum: int = Field(alias="numoc")  
    remito : str = Field(alias="remito", max_length=30)
    imp_total : Decimal = Field(alias="importe")
    nombreproveedor : str = Field(alias="nombreproveedor", max_length=100)
    nombrebodega : str = Field(alias="nombrebodega", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    ) 

# Modelo principal de respuesta del Monitor
class MonitorComprasRealizadas(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    # Usamos Any o dict para que 'detalles' acepte cualquier estructura de tabla
    detalles: List[Comprasrealizadas] 

    class Config:
        from_attributes = True

# ****************************************************** INICIO Reporte Costos
# Modelo principal de respuesta del Monitor
class MonitorCosto(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    # Usamos Any o dict para que 'detalles' acepte cualquier estructura de tabla
    detalles: List[DetalleCostos] 

    class Config:
        from_attributes = True   

# Modelo para cada tarjeta individual de KPI
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str 

class DetalleCostos(BaseModel):
    negocio: str = Field(alias="negocio")
    idbodega: int = Field(alias="idbodega")
    bodega: str = Field(alias="bodega")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    idarticulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    costo: Decimal = Field(alias="costo")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )        
# ****************************************************** FIN Reporte Costos

#Filtros General
class filtrosgenerales(BaseModel):
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