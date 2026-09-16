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
    fec_doc: datetime = Field(alias="fecha")
    status: bool = Field(alias="status")
    imp_base :  Decimal= Field(alias="impBase")
    usuario :  str = Field(alias="usuario", max_length=16)
    observacion : str = Field(alias="observacion", max_length=100)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]
    caja: Optional[CajaSimple] = None  #Solo aplica para la edicion del turno.

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)


class TurnoCreate(TurnoBase):
    pass

class ValidacionTurno(BaseModel):
    tieneturno : bool = Field(alias="tieneturno")
    id_sucursal_emp: int = Field(alias="idSucursal")
    id_turno : int = Field(alias="idTurno")
    fec_doc: datetime = Field(alias="Fecha")
    #datos de caja abierta.
    idbodega : int = Field(alias="idBodega")
    idestado : int = Field(alias="idEstado")
    documento : str = Field(alias="documento",max_length=10)
    nom_caja : str = Field(alias="nomCaja",max_length=100)
    cliente : Clienteturno = Field(alias="cliente")
    mediopago :  List[schema_medio.MedioPagoCombo]
    # turno_vencido: el turno SI existe (tieneturno=true) pero ya supero
    # horas_turno de la caja - las pantallas de venta deben bloquear en este caso
    # y mandar a cerrar el turno primero; el formulario de cierre en cambio ignora
    # este flag a proposito (un turno vencido igual se debe poder cerrar).
    turno_vencido: bool = Field(False, alias="turnoVencido")
    horas_transcurridas: Optional[float] = Field(None, alias="horasTranscurridas")
    horas_limite: Optional[int] = Field(None, alias="horasLimite")

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

class UltimaCajaxuser(BaseModel):
    id_turno : int = Field(alias="idturno")
    fec_doc: date = Field(alias="fecha")
    estado :str = Field(alias="estado",max_length=10)

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

# Esquema para paginacion
class PaginatedTurnoResponse(BaseModel):
    content: List[TurnoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

class TurnoPaginacion(BaseModel):
    id: int
    fec_doc: datetime = Field(alias="Fecha")
    usuario: str = Field(alias="Usuario", max_length=16)
    imp_base: Decimal = Field(alias="ImpBase")
    status: bool = Field(alias="Status")
    caja: CajaSimple

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class CajaSimple(BaseModel):
    nom_caja: str = Field(alias="nomCaja", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
