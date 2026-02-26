from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from datetime import datetime

class MotivoAjusteBase(BaseModel):
    cod_motivo: str
    nom_motivo: str
    signo: int
    activo: str
    cta_inventario: str
    logs: Optional[Any] = None

# Esquema para combos en la pagina Web
class MotivoCombo(BaseModel):
    id: int = Field(alias="idMotivo")
    cod_motivo: str = Field(alias="codMotivo", max_length=10)
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)   
    
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

class MotivoAjusteCreate(MotivoAjusteBase):
    pass

class MotivoAjusteResponse(MotivoAjusteBase):
    id: int
    fecha_mod: Optional[datetime]

    class Config:
        from_attributes = True