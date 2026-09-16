from pydantic import BaseModel, ConfigDict, Field


# Esquema para combos en la pagina Web (seleccion de formula en el formulario
# de Prestamo, y grilla de casillas en Configuracion de Prestamos).
class FormulaPrestamoCombo(BaseModel):
    id: int = Field(alias="id")
    codigo: str = Field(alias="codigo", max_length=30)
    nombre: str = Field(alias="nombre", max_length=80)
    genera_interes_mora: bool = Field(alias="generaInteresMora")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
