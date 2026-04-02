from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Schema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema para paginacion
class ServicioBase(BaseModel):
    id : int
    cod_servicio: str = Field(alias="codServicio", max_length=20)
    nom_servicio: str = Field(alias="nomServicio", max_length=50)    

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )