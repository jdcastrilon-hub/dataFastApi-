from pydantic import BaseModel, ConfigDict, Field
from typing import List

from app.modules.tesoreria.catalogos.periodicidad.schema_periodicidad import PeriodicidadCombo
from app.modules.tesoreria.catalogos.formulaprestamo.schema_formulaprestamo import FormulaPrestamoCombo


# Configuracion de Prestamos: singleton por empresa (patron m_confcomercial).
# En el guardado solo cuentan las dos listas de ids; catalogo_* son de solo
# lectura (el front pinta las casillas con eso) y se ignoran al guardar.
class ConfPrestamoBase(BaseModel):
    periodicidades_habilitadas: List[int] = Field(default=[], alias="periodicidadesHabilitadas")
    formulas_habilitadas: List[int] = Field(default=[], alias="formulasHabilitadas")

    catalogo_periodicidades: List[PeriodicidadCombo] = Field(default=[], alias="catalogoPeriodicidades")
    catalogo_formulas: List[FormulaPrestamoCombo] = Field(default=[], alias="catalogoFormulas")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
