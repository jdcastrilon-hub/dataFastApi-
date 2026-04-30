from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str    

    # --- Esquemas para la Cabecera ---
class AjusteBase(BaseModel):   
    id_trans: Optional[int] = Field(None,alias="idTrans") 
    id_emp : int = Field(alias="idEmp")
    id_bodega: int = Field(alias="idBodega")
    documento: str = Field(alias="documento", max_length=10)    
    fec_doc : datetime = Field(alias="fecDoc")
    id_articulo: int = Field(alias="idArticulo")
    observaciones: Optional[str] = Field(None, max_length=250)
    imp_costo_actual: Decimal= Field(alias="impCostoActual")
    imp_costo_nuevo: Decimal= Field(alias="impCostoNuevo")
    vista:  str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)