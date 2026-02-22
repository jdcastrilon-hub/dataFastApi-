from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, Json
from typing import List, Optional, Dict, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde
class ImpuestoBase(BaseModel):
    id: int = Field(alias="id") 
    id_tipo: int = Field(alias="tipoImpuesto")
    tasa_impu: str = Field(alias="tasaImpuesto", max_length=10)
    nombre_tasa: str = Field(alias="descripcionTasa", max_length=50)
    es_exenta: str = Field(alias="exenta", max_length=2)
    porc_tasa: Decimal = Field(alias="porcentaje")
    
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )
