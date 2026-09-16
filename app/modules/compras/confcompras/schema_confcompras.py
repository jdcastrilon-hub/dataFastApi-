from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


# --- Esquema auxiliar (solo lectura, ignorado al guardar) ---
class EstadoSimple(BaseModel):
    nom_estado: str = Field(alias="nomEstado", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Configuracion de compras (singleton por empresa) ---
class ConfComprasBase(BaseModel):
    id_emp: Optional[int] = Field(None, alias="idEmp")
    id_estado_comp: Optional[int] = Field(None, alias="idEstadoComp")
    act_precio_compra: bool = Field(False, alias="actPrecioCompra")
    # Ultimo nivel de la jerarquia de utilidad (subcategoria -> categoria ->
    # general en m_categoriasxutilidad). None = sin configurar (no sugiere).
    porc_utilidad_general: Optional[Decimal] = Field(None, alias="porcUtilidadGeneral", ge=0)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])
    estado_comp: Optional[EstadoSimple] = Field(None, alias="estadoComp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
