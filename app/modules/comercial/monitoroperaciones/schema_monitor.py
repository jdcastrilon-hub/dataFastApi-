from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class CajaComboSchema(BaseModel):
    id: int = Field(alias="idCaja")
    cod_caja: str = Field(alias="codCaja", max_length=15)
    nom_caja: str = Field(alias="nomCaja", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class SucursalCajasSchema(BaseModel):
    id: int = Field(alias="id")
    id_emp: int = Field(alias="idEmpresa")
    cod_sucursal: str = Field(alias="codSucursal")
    nom_sucursal: str = Field(alias="nomSucursal")
    cajas: List[CajaComboSchema] = Field(default=[], alias="cajas", validation_alias="caja")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class filtrosgenerales(BaseModel):
    idEmpresa: int
    listsucursales: List[SucursalCajasSchema] = []

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


# ****************************************************** INICIO Ventas Realizadas
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str


class VentaRealizada(BaseModel):
    id_trans: int
    nombre_sucursal: str = Field(alias="sucursal", max_length=80)
    tipo_documento: str = Field(alias="documento", max_length=50)
    # Concatenacion serie_docum+nro_docum (ej. "FE52"), mismo calculo que
    # previsualizarNumerador()/ModoEdicion() usan en el formulario de venta.
    factura: str = Field(alias="factura", max_length=30)
    fecha: date = Field(alias="fecha")
    nombre_cliente: str = Field(alias="cliente", max_length=100)
    # Nullable: una venta sin turno ni caja manual (dato historico inconsistente)
    # deja este campo sin resolver.
    nombre_caja: Optional[str] = Field(None, alias="caja", max_length=100)
    importe: Decimal = Field(alias="importe")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class MonitorVentasRealizadas(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    detalles: List[VentaRealizada]

    class Config:
        from_attributes = True
# ****************************************************** FIN Ventas Realizadas
