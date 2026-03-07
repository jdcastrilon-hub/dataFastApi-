from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime
from app.modules.stock.bodegas import schema_bodega

class SucursalBase(BaseModel):
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    id_ciudad: int = Field(alias="idCiudad")
    direccion: Optional[str] = Field(alias="direccion")
    telefono: Optional[str] = Field(alias="telefono")
    activo: str = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

#Lista Para combos
class SucursalListCombo(BaseModel):
    id: int = Field(alias="id")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

 #Lista Para combos
class SucursalListComboByBodegas(BaseModel):
    id: int = Field(alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    list_bodegas: List[schema_bodega.BodegaCombo]

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class SucursalCreate(SucursalBase):
    pass

class SucursalSchema(SucursalBase):
    id: int
    fecha_mod: Optional[datetime] = None

    class Config:
        from_attributes = True

# Para el paginador que mencionamos antes
class PaginatedSucursalResponse(BaseModel):
    items: List[SucursalSchema]
    total_records: int
    total_pages: int
    current_page: int
    page_size: int