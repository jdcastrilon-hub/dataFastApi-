from pydantic import BaseModel, Field
from typing import List, Optional


class MenuResponse(BaseModel):
    id_menu: int
    codigo: str
    nombre: str
    ruta: Optional[str] = None
    icono: Optional[str] = None
    es_contenedor: bool

    children: List["MenuResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


MenuResponse.model_rebuild()