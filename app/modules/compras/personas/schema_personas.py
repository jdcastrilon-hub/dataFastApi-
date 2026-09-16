from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import date, datetime
from typing import Optional, Any

# Detalle completo de una persona (usado para cargar sus datos, ej. al seleccionarla
# desde el buscador en proveedores/clientes/empleados). Los alias coinciden con los
# que ya usa el frontend (Persona.ts / PersonaComponent) para los datos de persona.
class PersonaDetalle(BaseModel):
    id_persona: int = Field(alias="idPersona")
    id_tipodoc: int = Field(alias="idTipoDoc")
    cod_tit: str = Field(alias="codigoTitular", max_length=50)
    nombres: str = Field(alias="nombres", max_length=60)
    apellidos: str = Field(alias="apellidos", max_length=60)
    nombre_completo: str = Field(alias="nombreCompleto", max_length=120)
    sexo: Optional[str] = Field(None, alias="sexo", max_length=2)
    fec_nacimiento: Optional[date] = Field(None, alias="fechaNacimiento")
    direccion: Optional[str] = Field(None, alias="direccion", max_length=50)
    telefono: Optional[str] = Field(None, alias="telefono", max_length=60)
    mail: Optional[str] = Field(None, alias="email", max_length=60)
    id_ciudad: int = Field(alias="idCiudad")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PersonaSearch(BaseModel):
    id_persona: int = Field(alias="idPersona")
    cod_tit: str = Field(alias="codTit", max_length=20)
    nombre_completo: str = Field(alias="nombreCompleto", max_length=80)

    class Config:
        from_attributes = True

# Fila de la tabla en el modal "Seleccionar persona"
class PersonaPaginacion(BaseModel):
    id_persona: int = Field(alias="idPersona")
    cod_tit: str = Field(alias="codTit", max_length=50)
    nombre_completo: str = Field(alias="nombreCompleto", max_length=120)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PaginatedPersonaResponse(BaseModel):
    content: list[PersonaPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int
