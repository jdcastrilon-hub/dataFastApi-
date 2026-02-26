from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# --- Esquemas para la Cabecera ---
class AjusteStockBase(BaseModel):
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_bodega: int = Field(alias="idBodega")
    documento: str = Field(alias="documento", max_length=10)
    nro_docum: int= Field(alias="nroDocum")
    id_calculo: int= Field(alias="idCalculo")
    fecha_movimiento: datetime = Field(alias="fechaMovimiento")
    id_estado: int= Field(alias="idEstado")
    id_motivo: int= Field(alias="idMotivo")
    observacion: Optional[str] = Field(alias="observacion", max_length=250)
    vista:  str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    detalles: List[DetalleAjusteBase] = Field(default=[], alias="detalles")
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

# --- Esquemas para el Detalle ---
class DetalleAjusteBase(BaseModel):
    #llave compuesta
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_articulo: int = Field(alias="idArticulo") 
    linea: int = Field(alias="linea")
    #campos
    id_ubicacion: int = Field(alias="idUbicacion")
    id_lote: int = Field(alias="idLote")
    cant_disp: int = Field(alias="cantDisp")
    cantidad: int = Field(alias="cantidad")

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class AjusteStockCreate(AjusteStockBase):
    pass # id_trans se hereda de la cabecera al insertar