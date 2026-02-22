from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Schema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema para paginacion
class CosteoBase(BaseModel):
    id : int
    tipo_costeo: str = Field(alias="tipoCosteo", max_length=20)
    nombre_costeo: str = Field(alias="nombreCosteo", max_length=50)    

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )