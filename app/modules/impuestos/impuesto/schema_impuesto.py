from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, Json
from typing import List, Optional, Dict, Any
from datetime import datetime

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# Esquema Molde (usado por /list, ya consumido por el formulario de articulos:
# no se le cambia la forma, solo se filtra por empresa por debajo)
class ImpuestoBase(BaseModel):
    id: int = Field(alias="id")
    id_tipo: int = Field(alias="tipoImpuesto")
    tasa_impu: str = Field(alias="tasaImpuesto", max_length=10)
    nombre_tasa: str = Field(alias="descripcionTasa", max_length=50)
    es_exenta: str = Field(alias="exenta", max_length=2)
    porc_tasa: Decimal = Field(alias="porcentaje")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Esquema para combos en la pagina Web (usado por compra-directa/venta-directa/
# venta-pos: no se le cambia la forma, solo se filtra por empresa por debajo)
class ImpuestoCombo(BaseModel):
    id: int
    tasa_impu: str = Field(alias="tasaImpuesto", max_length=10)
    porc_tasa: Decimal = Field(alias="porcentaje")
    nombre_tasa: str = Field(alias="descripcion", max_length=50)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# --- Esquemas para el maestro completo (CRUD) ---
class TipoImpuestoSimple(BaseModel):
    tipoimpu: str = Field(alias="codTipo", max_length=20)
    nombre_impuesto: str = Field(alias="nombreTipo", max_length=80)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ImpuestoCreate(BaseModel):
    # id_emp no se selecciona en el formulario: se envia silenciosamente desde
    # LoginService.getIdEmpresaActual() al guardar (patron "empresa de sesion").
    id_emp: int = Field(alias="idEmp")
    id_tipo: int = Field(alias="idTipo")
    tasa_impu: str = Field(alias="tasaImpuesto", max_length=10)
    nombre_tasa: str = Field(alias="nombreTasa", max_length=50)
    es_exenta: str = Field(alias="exenta", max_length=2)
    porc_tasa: Decimal = Field(alias="porcentaje")
    imp_minimo: Decimal = Field(alias="impMinimo")
    cuenta_vta: str = Field(alias="cuentaVenta", max_length=15)
    cuenta_cmp: str = Field(alias="cuentaCompra", max_length=15)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ImpuestoResponse(ImpuestoCreate):
    id: int = Field(alias="id")
    tipo_impuesto: Optional[TipoImpuestoSimple] = None

# Esquema para paginacion (fila de la tabla)
class ImpuestoPaginacion(BaseModel):
    id: int = Field(alias="id")
    tasa_impu: str = Field(alias="tasaImpuesto", max_length=10)
    nombre_tasa: str = Field(alias="nombreTasa", max_length=50)
    es_exenta: str = Field(alias="exenta", max_length=2)
    porc_tasa: Decimal = Field(alias="porcentaje")
    fecha_mod: Optional[datetime] = Field(alias="fechaMod", default=None)
    tipo_impuesto: Optional[TipoImpuestoSimple] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class PaginatedImpuestoResponse(BaseModel):
    content: List[ImpuestoPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# Catalogo de tipos de impuesto (solo lectura, sin CRUD propio) - alimenta el
# combo "Tipo de Impuesto" del formulario.
class TipoImpuestoCombo(BaseModel):
    id: int
    tipoimpu: str = Field(alias="codTipo", max_length=20)
    nombre_impuesto: str = Field(alias="nombreTipo", max_length=80)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
