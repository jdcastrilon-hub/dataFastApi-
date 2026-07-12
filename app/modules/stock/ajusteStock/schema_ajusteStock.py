from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import List, Optional, Any

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

# --- Esquemas para la Cabecera ---
class AjusteStockBase(BaseModel):
    id_trans: Optional[int] = Field(None,alias="idTrans")
    # No se selecciona: siempre es la empresa de la sesion actual (ver LoginService.getIdEmpresaActual()).
    id_emp: int = Field(alias="idEmpresa")
    id_bodega: int = Field(alias="idBodega")
    documento: str = Field(alias="documento", max_length=10)
    # Se autogenera desde el numerador de la empresa (ver CODIGO_NUMERADOR_AJUSTESTOCK);
    # opcional porque el formulario ya no lo tiene que enviar al crear.
    nro_docum: Optional[int] = Field(None, alias="nroDocum")
    id_calculo: int= Field(alias="idCalculo")
    fecha_movimiento: datetime = Field(alias="fechaMovimiento")
    id_estado: int= Field(alias="idEstado")
    id_motivo: int= Field(alias="idMotivo")
    observacion: Optional[str] = Field(alias="observacion", max_length=250)
    vista:  str = Field(alias="vista", max_length=16)
    fecha_mod: Optional[datetime] = Field(alias="fechaMod",default=None)
    detalles: List[DetalleAjusteBase] = Field(default=[], alias="detalles")
    # Lotes nuevos (aun no existen en m_lotes) creados durante la edicion de este ajuste.
    # Se materializan solo al guardar (ver sp_stock_impacto_ajustestock).
    nuevos_lotes: List[DetalleAjusteStockNuevoLote] = Field(default=[], alias="nuevosLotes")
    logs: List[LogEntry]

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True) 

# --- Esquemas para el Detalle ---
class DetalleAjusteBase(BaseModel):
    #llave compuesta
    id_trans: Optional[int] = Field(None,alias="idTrans")
    id_articulo: int = Field(alias="idArticulo") 
    id_codbarra: int = Field(alias="idCodBarra") 
    linea: int = Field(alias="linea")
    #campos
    id_ubicacion: int = Field(alias="idUbicacion")
    id_lote: int = Field(alias="idLote")
    cant_disp: int = Field(alias="cantDisp")
    cantidad: int = Field(alias="cantidad")
    articulo : Optional[ArticuloSimple] = None  #Solo aplica para la edicion de la compra.

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)

class DetalleAjusteStockNuevoLote(BaseModel):
    id_trans: Optional[int] = Field(None, alias="idTrans")
    id_articulo: int = Field(alias="idArticulo")
    id_lote: int = Field(alias="idLote")
    linea: Optional[int] = None

    codigo_lote: str = Field(alias="codigoLote", max_length=50)
    fec_vencimiento: date = Field(alias="fecVencimiento")

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True)

class AjusteStockCreate(AjusteStockBase):
    pass # id_trans se hereda de la cabecera al insertar

# Esquema para paginacion 
class PaginatedAjusteResponse(BaseModel):
    content: List[AjustePaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int


    # Esquema para paginacion
class AjustePaginacion(BaseModel):
    id_trans: int= Field(alias="idTrans")
    nro_docum: int= Field(alias="nroDocum")
    fecha_movimiento: datetime = Field(alias="fechaMovimiento")
    observacion :str = Field(alias="Observaciones")
    bodega : Optional[BodegaSimple] = None
    estado : Optional[EstadoSimple] = None 
    motivo : Optional[MotivoSimple] = None 

    

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class BodegaSimple(BaseModel):
    nom_bodega: str = Field(alias="nomBodega", max_length=80)    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class EstadoSimple(BaseModel):
    cod_estado: str = Field(alias="codEstado", max_length=20)    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MotivoSimple(BaseModel):
    nom_motivo: str = Field(alias="nomMotivo", max_length=80)    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ArticuloSimple(BaseModel):
    cod_barra: str = Field(alias="codArticulo" , max_length=50)
    ref_barra: str = Field(alias="nomArticulo" , max_length=100)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)