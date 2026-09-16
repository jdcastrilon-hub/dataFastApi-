from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Modelo para cada tarjeta individual de KPI (mismo shape que kpicompras/kpistock,
# duplicado a proposito - convencion ya establecida de no compartir entre monitores)
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str


class MovimientoTesoreria(BaseModel):
    id_trans: int = Field(alias="idTrans")
    linea: int = Field(alias="linea")
    fec_doc: date = Field(alias="fecha")
    tipo_cuenta: str = Field(alias="tipoCuenta")
    id_caja: Optional[int] = Field(None, alias="idCaja")
    nom_caja: Optional[str] = Field(None, alias="nomCaja")
    id_banco: Optional[int] = Field(None, alias="idBanco")
    nom_banco: Optional[str] = Field(None, alias="nomBanco")
    id_mediopago: int = Field(alias="idMediopago")
    tipo_mediopago: Optional[str] = Field(None, alias="tipoMediopago")
    concepto: str = Field(alias="concepto")
    vista: str = Field(alias="vista")
    id_referencia: int = Field(alias="idReferencia")
    importe: Decimal = Field(alias="importe")
    signo: int = Field(alias="signo")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class MonitorTesoreria(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    detalles: List[MovimientoTesoreria]

    model_config = ConfigDict(from_attributes=True)


# Esquemas simples para los combos de filtro (Caja/Banco/MedioPago) - propios de
# este monitor, no reutilizan los schemas completos de cada modulo.
class CajaSimple(BaseModel):
    id: int
    cod_caja: str = Field(alias="codCaja")
    nom_caja: str = Field(alias="nomCaja")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BancoSimple(BaseModel):
    id: int
    cod_banco: str = Field(alias="codBanco")
    nom_banco: str = Field(alias="nomBanco")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MedioPagoSimple(BaseModel):
    id: int
    tipo: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FiltrosTesoreria(BaseModel):
    idEmpresa: int
    listCajas: List[CajaSimple] = []
    listBancos: List[BancoSimple] = []
    listMediosPago: List[MedioPagoSimple] = []
    listVistas: List[str] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
