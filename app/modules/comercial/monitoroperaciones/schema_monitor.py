from datetime import date, datetime
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


class NegocioSchema(BaseModel):
    id: Optional[int] = Field(alias="idNegocio")
    cod_negocio: str = Field(alias="CodNegocio", max_length=10)
    nom_negocio: str = Field(alias="NomNegocio", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SubcategoriaSchema(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_subcategoria: str = Field(alias="codSubCategoria", max_length=20)
    nom_subcategoria: str = Field(alias="nomSubCategoria", max_length=50)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CategoriaSchema(BaseModel):
    id: Optional[int] = Field(alias="id")
    cod_categoria: str = Field(alias="codCategoria", max_length=20)
    nom_categoria: str = Field(alias="nomCategoria", max_length=20)
    subcategorias: List[SubcategoriaSchema] = Field(default=[], alias="subCategorias")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Solo listas base (id_cliente IS NULL) - una lista de cliente nunca se
# monitorea/ajusta desde esta pantalla, ver get_filtros.
class ListaPrecioSchema(BaseModel):
    id_lista: int = Field(alias="idLista")
    nombre: str = Field(alias="nombre", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class filtrosgenerales(BaseModel):
    idEmpresa: int
    listsucursales: List[SucursalCajasSchema] = []
    listnegocio: List[NegocioSchema] = []
    listCategorias: List[CategoriaSchema] = []
    listListaPrecio: List[ListaPrecioSchema] = []

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

# ****************************************************** INICIO Reporte Precios
class DetallePrecios(BaseModel):
    negocio: str = Field(alias="negocio")
    idlista: int = Field(alias="idlista")
    lista: str = Field(alias="lista")
    categoria: str = Field(alias="categoria")
    subcategoria: str = Field(alias="subcategoria")
    idarticulo: int = Field(alias="idarticulo")
    cod_articulo: str = Field(alias="codarticulo")
    nom_articulo: str = Field(alias="nomarticulo")
    precio: Decimal = Field(alias="precio")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class MonitorPrecio(BaseModel):
    totalElements: int
    totalPages: int
    number: int
    size: int
    kpis: List[KPICard]
    detalles: List[DetallePrecios]

    class Config:
        from_attributes = True


# Historial de un articulo en una lista: lee p_precios directo (ya es el
# ledger completo, sin necesidad de una tabla "kardex" aparte como en costos -
# p_precios no promedia, cada fila ya es un movimiento real de precio).
class PrecioHistorialLinea(BaseModel):
    fecha_mod: datetime = Field(alias="fechaMod")
    documento: Optional[str] = Field(None, alias="documento")
    nro_docum: Optional[int] = Field(None, alias="nroDocum")
    origen: str = Field(alias="origen")
    precio_anterior: Optional[Decimal] = Field(None, alias="precioAnterior")
    precio_nuevo: Decimal = Field(alias="precioNuevo")
    usuario_mod: Optional[str] = Field(None, alias="usuarioMod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
# ****************************************************** FIN Reporte Precios
