from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from . import repository_monitor, schema_monitor
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/monitoroperaciones",
    tags=["comercial - Monitor Operaciones"])


@router.get("/filtros", response_model=schema_monitor.filtrosgenerales)
def filtros(
    id_empresa: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    data = repository_monitor.get_filtros(db, id_empresa)

    if not data:
        return []

    return data


@router.get("/ventasrealizadas", response_model=schema_monitor.MonitorVentasRealizadas)
def get_ventasrealizadas(
    id_emp: int,
    fechainicial: date,
    fechafinal: date,
    id_sucursal: Optional[int] = 0,
    id_caja: Optional[int] = 0,
    tipos_documento: List[str] = Query([]),
    solo_con_descuento: bool = False,
    clientes: List[int] = Query([]),
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_ventasrealizadas_data(
        db, id_emp, fechainicial, fechafinal, id_sucursal, id_caja, page, size,
        tipos_documento, solo_con_descuento, clientes, articulos
    )


@router.get("/precios", response_model=schema_monitor.MonitorPrecio)
def get_precios(
    id_emp: int,
    lista: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_precios(db, id_emp, lista, negocio, categoria, subcategoria, page, size, articulos)


@router.get("/precios/export")
def exportar_precios(
    id_emp: int,
    lista: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_precios_export_data(db, id_emp, lista, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_precios(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="precios.xlsx"'}
    )


@router.get("/precios/historial", response_model=List[schema_monitor.PrecioHistorialLinea])
def get_precios_historial(
    id_emp: int,
    id_articulo: int,
    id_lista: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_precio_historial(db, id_emp, id_articulo, id_lista)
