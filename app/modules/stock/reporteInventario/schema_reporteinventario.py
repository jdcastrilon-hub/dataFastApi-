from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime
from app.modules.core.negocios import schema_negocio
from app.modules.core.sucursales import schema_sucursal


#Esquema empresas con lista de negocios
class EmpresaListaByNegocios(BaseModel):
    id_emp: int = Field(alias="idEmpresa") 
    nom_emp: str = Field(alias="nombreEmpresa", max_length=80)
    negocios: List[schema_negocio.NegocioCombo] = Field(default=[], alias="negocios")
    sucursales: List[schema_sucursal.SucursalListComboByBodegas] = Field(default=[], alias="sucursales")
   
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class InventarioxBodegaSchema(BaseModel):
    bodega: str = Field(alias="bodega")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    estado: str = Field(alias="estado")
    unidad: str = Field(alias="unidad")
    cantidad: float = Field(alias="cantidad")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


# Esquema para paginacion 
class PaginatedInventarioResponse(BaseModel):
    content: List[InventarioxBodegaSchema]
    totalElements: int
    totalPages: int
    number: int
    size: int