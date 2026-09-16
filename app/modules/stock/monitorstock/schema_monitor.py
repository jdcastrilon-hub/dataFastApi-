from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Optional
from app.modules.stock.bodegas import schema_bodega
from app.modules.stock.estados.schema_estado import EstadoCombo


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
    id_articulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    id_codbarra: int = Field(alias="idcodbarra")
    cod_barra: str = Field(alias="codbarra")
    estado: str = Field(alias="estado")
    unidad: str = Field(alias="unidad")
    cantidad: float = Field(alias="cantidad")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class MovimientoStock(BaseModel):
    fec_doc: date = Field(alias="fec_doc")
    documento: str = Field(alias="documento")
    nro_docum: int = Field(alias="nro_docum")
    bodega: str = Field(alias="bodega")
    estado: str = Field(alias="estado")
    tipo_movimiento: str = Field(alias="tipo_movimiento")
    cantidad: int = Field(alias="cantidad")
    vista: str = Field(alias="vista")
    fecha_mod: Optional[datetime] = Field(default=None, alias="fecha_mod")
    usuario_mod: Optional[str] = Field(default=None, alias="usuario_mod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Modelo principal de respuesta de Valoracion de Inventario
class MonitorValoracion(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    valorTotalInventario: float
    detalles: List[ValoracionDisponible]

    class Config:
        from_attributes = True

class ValoracionDisponible(BaseModel):
    negocio: str = Field(alias="negocio")
    bodega: str = Field(alias="bodega")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    id_articulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    unidad: str = Field(alias="unidad")
    cantidad: float = Field(alias="cantidad")
    costo_unitario: float = Field(alias="costounitario")
    valor_total: float = Field(alias="valortotal")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Modelo principal de respuesta de Stock Minimo (alertas de reposicion)
class MonitorStockMinimo(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    totalFaltante: float
    detalles: List[StockMinimoDisponible]

    class Config:
        from_attributes = True

class StockMinimoDisponible(BaseModel):
    negocio: str = Field(alias="negocio")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    id_articulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    unidad: str = Field(alias="unidad")
    cantidad_disponible: float = Field(alias="cantidaddisponible")
    stock_minimo: float = Field(alias="stockminimo")
    stock_maximo: Optional[float] = Field(None, alias="stockmaximo")
    faltante: float = Field(alias="faltante")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Modelo principal de respuesta de Vencimientos Proximos (alertas de lotes por vencer)
class MonitorVencimientos(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    totalUnidadesEnRiesgo: float
    detalles: List[LoteVencimiento]

    class Config:
        from_attributes = True

class LoteVencimiento(BaseModel):
    negocio: str = Field(alias="negocio")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    id_articulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    bodega: str = Field(alias="bodega")
    codigo_lote: str = Field(alias="codigolote")
    fec_vencimiento: date = Field(alias="fecvencimiento")
    dias_para_vencer: int = Field(alias="diasparavencer")
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
    listestados: List[EstadoCombo] = []
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