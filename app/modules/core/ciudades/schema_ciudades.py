from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class CiudadBase(BaseModel):
    id_departamento: int = Field(..., alias="idDepartamento")
    cod_ciudad: str = Field(..., alias="codCiudad", max_length=10)
    nom_ciudad: str = Field(..., alias="nomCiudad", max_length=50)

    class Config:
        # Esto permite que FastAPI acepte tanto id_departamento como idDepartamento
        populate_by_name = True

# Esquema para paginacion
class CiudadCombo(BaseModel):
    id_ciudad : int = Field(alias="idCiudad")
    cod_ciudad: str = Field(..., alias="codCiudad", max_length=10)
    nom_ciudad: str = Field(..., alias="nomCiudad", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )        

class CiudadCreate(CiudadBase):
    pass

class CiudadResponse(CiudadBase):
    id_ciudad: int = Field(..., alias="idCiudad")

    class Config:
        from_attributes = True # Reemplaza a orm_mode = True en Pydantic V2