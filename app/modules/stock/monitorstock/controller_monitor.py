from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from . import repository_monitor, schema_monitor
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/monitor",
    tags=["Bodega - Monitor"])

@router.get("/filtrovista1", response_model=schema_monitor.filtrosgeneralesxempresa)
def filtrosvista1(id_empresa: int,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):

    data = repository_monitor.get_filtros_vista_inventario(db,id_empresa)
    
    if not data:
        # Devolver lista vacia , si no hay data
        return []
        
    return data


@router.get("/inventario", response_model=schema_monitor.MonitorInventario)
def get_monitorcomprasrealizadas_data(
   # tipo_reporte: str,
    id_emp: int,
    bodega: int,
    negocio : int,
    categoria: int,
    subcategoria : int,
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    print ("get_monitorcomprasrealizadas_data")
    return repository_monitor.get_monitorinventario_data(db, id_emp, bodega, negocio,categoria,subcategoria,page,size,articulos)


@router.get("/kardex", response_model=List[schema_monitor.MovimientoStock])
def get_kardex(
    id_articulo: int,
    id_codbarra: int,
    fecha_inicial: Optional[date] = None,
    fecha_final: Optional[date] = None,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_kardex_articulo(db, id_articulo, id_codbarra, fecha_inicial, fecha_final)


@router.get("/inventario/export")
def exportar_inventario(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_inventario_export_data(db, id_emp, bodega, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_inventario(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="inventario.xlsx"'}
    )


@router.get("/valoracion", response_model=schema_monitor.MonitorValoracion)
def get_valoracion(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_valoracion_data(db, id_emp, bodega, negocio, categoria, subcategoria, page, size, articulos)


@router.get("/valoracion/export")
def exportar_valoracion(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_valoracion_export_data(db, id_emp, bodega, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_valoracion(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="valoracion.xlsx"'}
    )


@router.get("/stockminimo", response_model=schema_monitor.MonitorStockMinimo)
def get_stockminimo(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_stockminimo_data(db, id_emp, bodega, negocio, categoria, subcategoria, page, size, articulos)


@router.get("/stockminimo/export")
def exportar_stockminimo(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_stockminimo_export_data(db, id_emp, bodega, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_stockminimo(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="stock_minimo.xlsx"'}
    )


@router.get("/vencimientos", response_model=schema_monitor.MonitorVencimientos)
def get_vencimientos(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_vencimientos_data(db, id_emp, bodega, negocio, categoria, subcategoria, page, size, articulos)


@router.get("/vencimientos/export")
def exportar_vencimientos(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_vencimientos_export_data(db, id_emp, bodega, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_vencimientos(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="vencimientos.xlsx"'}
    )
