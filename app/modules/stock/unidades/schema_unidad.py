from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class UnidadBase(BaseModel):
    id: int = Field(alias="id") 
    cod_unidad: str = Field(alias="codUnidad", max_length=10)
    nom_unidad: str = Field(alias="nomUnidad", max_length=50)


    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )
