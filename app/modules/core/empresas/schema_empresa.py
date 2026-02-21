from pydantic import BaseModel, ConfigDict, Field, Json
from typing import List, Optional, Dict, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Lista
class EmpresaListaCombo(BaseModel):
    id_emp: int = Field(alias="id_emp") 
    nom_emp: str = Field(alias="nomEmp", max_length=20)
    razon_social: str = Field(alias="razonSocial", max_length=80)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

#Esquema empresas con lista de negocios
class EmpresaListaByNegocios(BaseModel):
    id_emp: int = Field(alias="id_emp") 
    nom_emp: str = Field(alias="nomEmp", max_length=20)
    razon_social: str = Field(alias="razonSocial", max_length=80)
    negocios: List[ListaNegocios] = Field(default=[], alias="negocios")
   
    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )

class ListaNegocios(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_negocio:  str = Field(alias="codNegocio", max_length=20)
    nom_negocio:  str = Field(alias="nomNegocio", max_length=20)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True
    )