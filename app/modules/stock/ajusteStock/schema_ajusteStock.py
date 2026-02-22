from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional, Any

# --- Esquemas para el Detalle ---
class DetalleAjusteBase(BaseModel):
    id_articulo: int
    linea: int
    id_ubicacion: int
    id_lote: int
    cant_disp: int
    cantidad: int

class DetalleAjusteCreate(DetalleAjusteBase):
    pass # id_trans se hereda de la cabecera al insertar

class DetalleAjusteResponse(DetalleAjusteBase):
    id_trans: int
    model_config = ConfigDict(from_attributes=True)

# --- Esquemas para la Cabecera ---
class AjusteStockBase(BaseModel):
    id_bodega: int
    documento: str
    nro_docum: int
    id_calculo: int
    fecha_movimiento: date
    id_estado: int
    id_motivo: int
    observacion: Optional[str] = None
    vista: str
    fecha_mod: datetime
    logs: Optional[Any] = None

class AjusteStockCreate(AjusteStockBase):
    # Incluimos los detalles para creación anidada
    detalles: List[DetalleAjusteCreate]

class AjusteStockResponse(AjusteStockBase):
    id_trans: int
    detalles: List[DetalleAjusteResponse]
    model_config = ConfigDict(from_attributes=True)