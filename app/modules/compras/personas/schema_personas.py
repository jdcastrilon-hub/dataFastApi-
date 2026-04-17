from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional, Any

class PersonaBase(BaseModel):
    id_tipodoc: int = Field(..., alias="idTipoDoc")
    cod_tit: str = Field(..., alias="codTit", max_length=50)
    nombres: str = Field(..., max_length=60)
    apellidos: str = Field(..., max_length=60)
    nombre_completo: str = Field(..., alias="nombreCompleto", max_length=120)
    sexo: Optional[str] = Field(None, max_length=2)
    fec_nacimiento: Optional[date] = Field(None, alias="fecNacimiento")
    direccion: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=60)
    mail: Optional[str] = Field(None, max_length=60)
    id_ciudad: int = Field(..., alias="idCiudad")
    logs: Optional[Any] = None

    class Config:
        populate_by_name = True

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    id_persona: int = Field(..., alias="idPersona")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    class Config:
        from_attributes = True

class PersonaSearch(BaseModel):
    id_persona: int = Field(alias="idPersona") 
    cod_tit: str = Field(alias="codTit", max_length=20)
    nombre_completo: str = Field(alias="nombreCompleto", max_length=80)

    class Config:
        from_attributes = True      
