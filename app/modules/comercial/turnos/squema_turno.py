from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any
from decimal import Decimal
from app.modules.comercial.mediopago import schema_medio

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class TurnoBase(BaseModel):
    id : Optional[int] = Field(None,alias="id") 
    id_caja : int = Field(alias="idCaja")
    fec_doc: datetime = Field(alias="Fecha")
    status: bool = Field(alias="status")
    imp_base :  Decimal= Field(alias="impBase")
    usuario :  str = Field(alias="usuario", max_length=16)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)


class TurnoCreate(TurnoBase):
    pass

class ValidacionTurno(BaseModel):
    tieneturno : bool = Field(alias="tieneturno")
    id_turno : int = Field(alias="idTurno")
    fec_doc: datetime = Field(alias="Fecha")
    #datos de caja abierta.
    idbodega : int = Field(alias="idBodega")
    idestado : int = Field(alias="idEstado")
    documento : str = Field(alias="documento",max_length=10)
    nom_caja : str = Field(alias="nomCaja",max_length=100)
    cliente : Clienteturno = Field(alias="cliente")
    mediopago :  List[schema_medio.MedioPagoCombo]
    
    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class Clienteturno(BaseModel):
    id_cliente: Optional[int] = Field(None, alias="idCliente")
    id_persona: Optional[int] = Field(None, alias="idPersona")
    cod_tit: str = Field(alias="codTit", max_length=50)
    nom_cliente: str = Field(alias="nombreCompleto", max_length=100)
    
    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)
