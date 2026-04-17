from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class ProveedorBase(BaseModel):
    id_emp : int  = Field(alias="idEmp")
    id_proveedor: Optional[int] = Field(None, alias="idProveedor")
    id_persona: Optional[int] = Field(None, alias="idPersona")
    cod_tit: str = Field(alias="codigoTitular", max_length=50)
    razon_social: str = Field(alias="razonSocial", max_length=150)
    regimen: str = Field(alias="regimen", max_length=20)
    activo: str = Field(alias="activo", max_length=2)
    observacion: str = Field(alias="observacion", max_length=250)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    logs: List[LogEntry]
    persona:  PersonaBase= Field(default=[], alias="persona")

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class PersonaBase(BaseModel):    
    id_tipodoc: int = Field(alias="idTipoDoc")
    cod_tit:  str = Field(alias="codigoTitular", max_length=50)
    nombres: str = Field(alias="nombres", max_length=60)
    apellidos: str = Field(alias="apellidos", max_length=60)
    nombre_completo:  str = Field(alias="nombreCompleto", max_length=120)
    sexo: str = Field(alias="sexo", max_length=2)
    fec_nacimiento: Optional[date] = Field(None, alias="fechaNacimiento")
    direccion:  str = Field(alias="direccion", max_length=50)
    telefono:  str = Field(alias="telefono", max_length=60)
    mail: str = Field(alias="email", max_length=60)
    id_ciudad:  int = Field(alias="idCiudad")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class ProveedorCreate(ProveedorBase):
    pass


class ProveedorSearch(BaseModel):
    id_proveedor: int = Field(alias="idProveedor") 
    id_persona: int = Field(alias="idPersona") 
    cod_tit: str = Field(alias="codTit", max_length=20)
    razon_social: str = Field(alias="nombreCompleto", max_length=80)

    class Config:
        from_attributes = True       

# Esquema para paginacion 
class PaginatedProveedorResponse(BaseModel):
    content: List[ProveedorPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int 


    # Esquema para paginacion
class ProveedorPaginacion(BaseModel):
    id_proveedor : int
    cod_tit: str = Field(alias="codBodega", max_length=50)
    razon_social: str = Field(alias="nomBodega", max_length=150)
    activo: str = Field(alias="activo", max_length=2)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
  

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )
