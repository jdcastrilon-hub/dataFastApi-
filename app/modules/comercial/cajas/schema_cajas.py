from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class CajaXUserBase(BaseModel):    
    usuario: str = Field(alias="usuario", max_length=16)

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class CajaBase(BaseModel):
    id_emp : int  = Field(alias="idEmp")
    id_sucursal_emp: int = Field(alias="idSucursal")
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)
    cajapos: bool = Field(alias="cajaPos")
    status: bool = Field(alias="status")
    id_cliente : int = Field(alias="idCliente")
    id_bodega : int = Field(alias="idBodega")
    id_estado : int = Field(alias="idEstado")
    documento : str = Field(alias="documento", max_length=10)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]
    usuarios:  List[CajaXUserBase] = Field(default=[], alias="usuarios")

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class CajaCreate(CajaBase):
    pass


# Esquema para combos en la pagina Web
class CajaCombo(BaseModel):
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )