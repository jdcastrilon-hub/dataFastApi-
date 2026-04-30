from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class ClienteBase(BaseModel):
    id_emp : int  = Field(alias="idEmp")
    id_cliente: Optional[int] = Field(None, alias="idCliente")
    id_persona: Optional[int] = Field(None, alias="idPersona")
    cod_tit: str = Field(alias="codigoTitular", max_length=50)
    nom_cliente: str = Field(alias="nomCliente", max_length=100)
    direccion: str = Field(alias="direccion", max_length=50)
    mail: str = Field(alias="mail", max_length=50)
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

class ClienteCreate(ClienteBase):
    pass