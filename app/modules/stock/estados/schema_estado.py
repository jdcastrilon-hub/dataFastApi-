from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from datetime import datetime

class EstadoBase(BaseModel):
    cod_estado: str = Field(..., max_length=20)
    nom_estado: str = Field(..., max_length=80)
    activo: str = Field(..., max_length=2)
    loteable: str = Field(..., max_length=2)
    tiene_ubicaciones: str = Field(..., max_length=2)
    unidades_negativas: str = Field(..., max_length=2)
    obervacion: str = Field(..., max_length=250)
    logs: Optional[Any] = None

# Esquema para combos en la pagina Web
class EstadoCombo(BaseModel):
    id: int = Field(alias="id")
    cod_estado: str = Field(alias="codEstado", max_length=10)
    nom_estado: str = Field(alias="nomEstado", max_length=80)   
    
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class EstadoCreate(EstadoBase):
    pass

class EstadoResponse(EstadoBase):
    id: int
    fecha_mod: Optional[datetime]

    class Config:
        from_attributes = True