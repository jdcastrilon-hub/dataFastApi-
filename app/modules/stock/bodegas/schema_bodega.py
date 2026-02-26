from pydantic import BaseModel, ConfigDict, Field, Json
from typing import List, Optional, Dict, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class BodegaBase(BaseModel):
    id_sucursal: int = Field(alias="idSucursal") 
    cod_bodega: str = Field(alias="codBodega", max_length=20)
    nom_bodega: str = Field(alias="nomBodega", max_length=80)
    principal: str = Field(alias="bodegaPrincipal", max_length=2, description="SI/NO o S/N")
    tiene_ubicaciones: str = Field(alias="manejaUbicaciones", max_length=2)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

# Esquema para paginacion
class BodegaPaginacion(BaseModel):
    id : int
    cod_bodega: str = Field(alias="codBodega", max_length=20)
    nom_bodega: str = Field(alias="nomBodega", max_length=80)
    principal: str = Field(alias="bodegaPrincipal", max_length=2, description="SI/NO o S/N")
    tiene_ubicaciones: str = Field(alias="manejaUbicaciones", max_length=2)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
  

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )


# Esquema para paginacion 
class PaginatedBodegaResponse(BaseModel):
    content: List[BodegaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Esquema para combos en la pagina Web
class BodegaCombo(BaseModel):
    id: int
    cod_bodega: str = Field(alias="codBodega", max_length=20)
    nom_bodega: str = Field(alias="nomBodega", max_length=80)   
    tiene_ubicaciones: str = Field(alias="manejaUbicaciones", max_length=2)
    

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

    
# Esquema para crear (lo que recibe el POST)
class BodegaCreate(BodegaBase):
    pass

# Esquema para la respuesta (lo que devuelve el GET)
class BodegaResponse(BodegaBase):
    id: int
    
# Esquema para reportes*****************************
# Esquema Stock Disponible
class StockDisponibleResponse(BaseModel):
    idArticulo: int
    codArticulo: str
    nomArticulo: str
    ubicacion: Optional[str] = None
    lote: Optional[str] = None
    stock: float

    class Config:
        from_attributes = True    