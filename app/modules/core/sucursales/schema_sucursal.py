from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import datetime
from app.modules.stock.bodegas import schema_bodega
from app.modules.comercial.documentos import schema_docum
from app.modules.comercial.mediopago import schema_medio
from app.modules.comercial.cajas import schema_cajas

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class UsuarioSimple(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SucursalXUsuarioBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: Optional[UsuarioSimple] = None  # Solo se completa al leer (join), se ignora al guardar.

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class SucursalBase(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    id_ciudad: int = Field(alias="idCiudad")
    direccion: Optional[str] = Field(None, alias="direccion")
    telefono: Optional[str] = Field(None, alias="telefono")
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry] = Field(default=[])
    usuarios: List[SucursalXUsuarioBase] = Field(default=[], alias="usuarios")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para paginacion (lista de la pestaña Sucursales de Administracion)
class SucursalPaginacion(BaseModel):
    id: int = Field(alias="id")
    cod_sucursal: str = Field(alias="codSucursal", max_length=20)
    nom_sucursal: str = Field(alias="nomSucursal", max_length=80)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

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
    list_bodegas: List[schema_bodega.BodegaCombo] = Field(
        alias="list_bodegas", 
        validation_alias="bodegas" 
    )
    documentos : List[schema_docum.DocumentCombo]
    mediopago :  List[schema_medio.MedioPagoCombo]

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class SucursalCreate(SucursalBase):
    pass

class PaginatedSucursalResponse(BaseModel):
    content: List[SucursalPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

 #Lista Para combos x cajas
class SucursalListComboByCajas(BaseModel):
    id: int = Field(alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str  = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    cajas: List[schema_cajas.CajaCombo]

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )    