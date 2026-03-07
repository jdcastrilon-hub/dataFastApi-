from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class TipoDocumentoBase(BaseModel):    
    cod_tipodoc: str = Field(alias="codigoTipoDocumento", max_length=20)
    nom_tipodoc: str = Field(alias="nombreTipoDocumento", max_length=80)   
    
    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

 # Esquema para combos en la pagina Web
class TipoDocCombo(BaseModel):
    id: int
    cod_tipodoc: str = Field(alias="codigoTipoDocumento", max_length=20)
    nom_tipodoc: str = Field(alias="nombreTipoDocumento", max_length=80)   
    
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )


class TipoDocumentoCreate(TipoDocumentoBase):
    pass

class TipoDocumentoResponse(TipoDocumentoBase):
    id: int
    fecha_mod: datetime

    class Config:
        from_attributes = True