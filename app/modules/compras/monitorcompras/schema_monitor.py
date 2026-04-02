from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Optional

# Modelo para cada tarjeta individual de KPI
class KPICard(BaseModel):
    titulo: str
    valor: str
    icono: str
    color: str

class Comprasrealizadas(BaseModel):
    id_trans : int
    fec_doc: date = Field(alias="fecha")  
    nro_docum: int = Field(alias="numoc")  
    remito : str = Field(alias="remito", max_length=30)
    imp_total : Decimal = Field(alias="importe")
    nombreproveedor : str = Field(alias="nombreproveedor", max_length=100)
    nombrebodega : str = Field(alias="nombrebodega", max_length=100)

    model_config = ConfigDict(
        from_attributes=True,  
        populate_by_name=True   
    )

# Modelo principal de respuesta del Monitor
class MonitorComprasRealizadas(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    # Usamos Any o dict para que 'detalles' acepte cualquier estructura de tabla
    detalles: List[Comprasrealizadas] 

    class Config:
        from_attributes = True