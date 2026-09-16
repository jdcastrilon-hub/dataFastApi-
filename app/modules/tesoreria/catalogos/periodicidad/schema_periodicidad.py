from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


# Esquema para combos en la pagina Web (seleccion de periodicidad en el
# formulario de Prestamo, y grilla de casillas en Configuracion de Prestamos).
class PeriodicidadCombo(BaseModel):
    id: int = Field(alias="id")
    nombre: str = Field(alias="nombre", max_length=50)
    dias: int = Field(alias="dias")
    observacion: Optional[str] = Field(alias="observacion", max_length=250, default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
