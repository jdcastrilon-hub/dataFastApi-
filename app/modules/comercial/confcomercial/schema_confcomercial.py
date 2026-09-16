from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str


# --- Esquemas auxiliares (solo lectura, ignorados al guardar) ---
class RolSimple(BaseModel):
    id_rol: int = Field(alias="idRol")
    nombre: str = Field(alias="nombre", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Grilla de "que rol puede aplicar descuento y hasta cuanto" ---
class DctoRolBase(BaseModel):
    id_rol: int = Field(alias="idRol")
    max_descuento: Decimal = Field(alias="maxDescuento")
    rol: Optional[RolSimple] = None  # Solo se llena al leer (join); se ignora al guardar.

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Configuracion comercial (singleton por empresa) ---
class ConfComercialBase(BaseModel):
    id_emp: Optional[int] = Field(None, alias="idEmp")
    precio_cero_editable: bool = Field(False, alias="precioCeroEditable")
    # Placeholders: sin funcionalidad propia todavia (reimpresion de factura,
    # devolucion de venta) - ver project_data_confcomercial.
    reimpresion_factura_permitida: bool = Field(False, alias="reimpresionFacturaPermitida")
    id_bodega_devoluciones: Optional[int] = Field(None, alias="idBodegaDevoluciones")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry] = Field(default=[])
    # Grilla completa "rol -> max % descuento" - se borra e reinserta entera en
    # cada guardado (mismo patron ya usado para m_listaprecioxuser/detalles de
    # venta), una sola llamada de guardado para todo el formulario.
    roles_descuento: List[DctoRolBase] = Field(default=[], alias="rolesDescuento")
    bodega_devoluciones: Optional[BodegaSimple] = Field(None, alias="bodegaDevoluciones")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
