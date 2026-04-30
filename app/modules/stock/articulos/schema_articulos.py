from pydantic import BaseModel, ConfigDict, Field, Json, model_validator
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
    id_negocio: int = Field(alias="idNegocio") 
    id_categoria: int = Field(alias="idCategoria") 
    id_subcategoria: int = Field(alias="idsubCategoria") 
    id_unidad: int = Field(alias="idunidad") 
    id_tiposervicio: int = Field(alias="idTipoService") 
    id_impuesto: int = Field(alias="idImpuesto") 
    id_ref: int = Field(alias="idRef")     
    activo_stock: bool = Field(alias="activoStock")
    stock_min: Optional[int]  = Field(alias="stockMin") 
    stock_max: Optional[int]  = Field(alias="stockMax")     
    grupo_contable: str = Field(alias="grupoContable", max_length=20)
    cta_inventario: Optional[str]  = Field(alias="cuentaInventario", max_length=15)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    codigosBarra: List[CodigoBarraBase]
    logs: List[LogEntry]
    objnegocio: Optional[Negocio] = None # Aplicar para recuperar informacion del articulo

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class CodigoBarraBase(BaseModel):
    id_codbarra: Optional[int] = Field(None,alias="idCodBarra") 
    id_articulo: Optional[int] = Field(None,alias="idArticulo") 
    cod_barra: str = Field(alias="codBarra", max_length=50)
    ref_barra: str = Field(alias="nomBarra", max_length=100)
    estado: bool = Field(alias="estado"),
    registro_nuevo : bool= Field(alias="registro_nuevo"),

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

# Esquema para crear (lo que recibe el POST)
class ArticuloCreate(ArticulosBase):
    pass


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
    id: Optional[int] = Field(alias="idNegocio")
    cod_negocio:  str = Field(alias="Codnegocio", max_length=10)
    nom_negocio:  str = Field(alias="NomNegocio", max_length=100)

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

# Esquema para paginacion 
class PaginatedArticuloResponse(BaseModel):
    content: List[ArticuloPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para paginacion
class ArticuloPaginacion(BaseModel):
    id_articulo: int
    cod_articulo: str = Field(alias="codArticulo")
    nom_articulo: str = Field(alias="nomArticulo")
    activo_stock: bool = Field(alias="activoStock")
    
    # Campos aplanados
    nom_subcategoria: str = Field(alias="nomSubCategoria")
    nom_categoria: str = Field(alias="nomCategoria")
    nom_negocio: str= Field(alias="nomNegocio")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_categories(cls, data):
        # 'data' es la instancia de la clase 'Articulo' de SQLAlchemy
        if hasattr(data, 'subcategoria') and data.subcategoria:
            # Seteamos el nombre de la subcategoría
            setattr(data, 'nom_subcategoria', data.subcategoria.nom_subcategoria)
            
            # Navegamos un nivel más hacia la categoría (parent)
            if hasattr(data.subcategoria, 'parent') and data.subcategoria.parent:
                setattr(data, 'nom_categoria', data.subcategoria.parent.nom_categoria)
        
        # Procesar Negocio
        neg = getattr(data, 'objnegocio', None)
        if neg:
        # IMPORTANTE: Revisa si en tu tabla Negocio la columna se llama 'nom_negocio' o 'negocio'
        # Según tu código anterior, parece que el campo de texto se llama 'negocio'
         setattr(data, 'nom_negocio', getattr(neg, 'nom_negocio', ""))

        return data
    
# Esquema para actualizacion masiva de stock
class ArticuloActualizacionDatos(BaseModel):    
    idcodbarra: int
    stock: int
    movimientos: int

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )