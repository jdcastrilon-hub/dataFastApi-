from pydantic import BaseModel, ConfigDict, Field, Json
from typing import List, Optional, Dict, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Lista
class ArticulosBase(BaseModel):
    id_articulo: Optional[int] = Field(alias="id_articulo") 
    cod_articulo: str = Field(alias="codArticulo", max_length=30)
    nom_articulo: str = Field(alias="nomArticulo", max_length=100)
    tipo_producto: str = Field(alias="TipoProducto", max_length=2)
    id_negocio: int = Field(alias="idNegocio") 
    id_categoria: int = Field(alias="idCategoria") 
    id_subcategoria: int = Field(alias="idsubCategoria") 
    id_unidad: int = Field(alias="idunidad") 
    id_costeo: int = Field(alias="idCosteo") 
    id_impuesto: int = Field(alias="idImpuesto") 
    id_ref: int = Field(alias="idRef")     
    activo_stock: str = Field(alias="activoStock", max_length=2)
    stock_min: Optional[int]  = Field(alias="stockMin") 
    stock_max: Optional[int]  = Field(alias="stockMax")     
    activo_comercial: str = Field(alias="activoComercial", max_length=2)
    grupo_contable: str = Field(alias="grupoContable", max_length=20)
    cta_inventario: Optional[str]  = Field(alias="cuentaInventario", max_length=15)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    codigosBarra: List[CodigoBarraBase]
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class CodigoBarraBase(BaseModel):
    id_codbarra: Optional[int] = Field(None,alias="id") 
    id_articulo: Optional[int] = Field(None,alias="idArticulo") 
    cod_barra: str = Field(alias="codBarra", max_length=50)
    ref_barra: str = Field(alias="nomBarra", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )


#Esquema empresas con lista de negocios
class ArticuloBaseCompleto(BaseModel):
    id_articulo: int = Field(alias="idArticulo") 
    cod_articulo: str = Field(alias="codArticulo", max_length=20)
    nom_articulo: str = Field(alias="nomArticulo", max_length=80)
    id_negocio : int = Field(alias="idNegocio")
    negocio: Optional[Negocio] = None
    subcategoria: Optional[SubCategoria] = None
    unidad : Optional[Unidad]=None

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class Negocio(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_negocio:  str = Field(alias="codNegocio", max_length=20)
    nom_negocio:  str = Field(alias="nomNegocio", max_length=20)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class SubCategoria(BaseModel):
    categoria_id: Optional[int] = Field(alias="idCategoria")
    cod_subcategoria:  str = Field(alias="codSubcategoria", max_length=20)
    nom_subcategoria:  str = Field(alias="nomSubcategoria", max_length=20)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class Unidad(BaseModel):
    id: Optional[int] = Field(alias="idUnidad")
    cod_unidad:  str = Field(alias="codUnidad", max_length=20)
    nom_unidad:  str = Field(alias="nomUnidad", max_length=20)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class ArticuloSearchCodigoBarra(BaseModel):
    id_articulo: int = Field(alias="idArticulo") 
    id_codbarra: int = Field(alias="idCodBarra") 
    cod_articulo: str = Field(alias="codArticulo", max_length=20)
    nom_articulo: str = Field(alias="nomArticulo", max_length=80)

    class Config:
        from_attributes = True

class ArticuloSearchCodigoStock(BaseModel):
    id_articulo: int = Field(alias="idArticulo") 
    cod_articulo: str = Field(alias="codArticulo", max_length=20)
    nom_articulo: str = Field(alias="nomArticulo", max_length=80)

    class Config:
        from_attributes = True

class GeneracionCodigoBarra(BaseModel):        
    id_articulo: int = Field(alias="idArticulo") 
    id_codbarra: int = Field(alias="idCodBarra")     
    existe : bool = Field(alias="existe")  

    class Config:
        from_attributes = True

# Esquema para crear (lo que recibe el POST)
class ArticuloCreate(ArticulosBase):
    pass