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
    prefix="/compras/monitor",
    tags=["compras - Monitor"])

@router.get("/filtros", response_model=schema_monitor.filtrosgenerales)
def filtros(id_empresa: int,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):

    data = repository_monitor.get_filtros(db,id_empresa)
    
    if not data:
        # Devolver lista vacia , si no hay data
        return []
        
    return data

@router.get("/comprasrealizadas", response_model=schema_monitor.MonitorComprasRealizadas)
def get_monitorcomprasrealizadas_data(
    id_emp: int,
    fechainicial: date,
    fechafinal: date,
    id_sucursal: Optional[int] = 0,
    id_bodega: Optional[int] = 0,
    articulos: List[int] = Query([]),
    proveedores: List[int] = Query([]),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_monitorcomprasrealizadas_data(db, id_emp, fechainicial, fechafinal, id_sucursal, id_bodega, page, size, articulos, proveedores)


@router.get("/comprasrealizadas/export")
def exportar_comprasrealizadas(
    id_emp: int,
    fechainicial: date,
    fechafinal: date,
    id_sucursal: Optional[int] = 0,
    id_bodega: Optional[int] = 0,
    articulos: List[int] = Query([]),
    proveedores: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_comprasrealizadas_export_data(db, id_emp, fechainicial, fechafinal, id_sucursal, id_bodega, articulos, proveedores)
    buffer = repository_monitor.generar_excel_comprasrealizadas(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="compras_realizadas.xlsx"'}
    )

@router.get("/comprasrealizadas/detalle", response_model=List[schema_monitor.DetalleCompraLinea])
def get_detalle_compra(
    nro_trans: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_detalle_compra(db, nro_trans)


@router.get("/comprasrealizadas/devoluciones", response_model=List[schema_monitor.DevolucionCompraLinea])
def get_devoluciones_compra(
    nro_trans: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_monitor.get_devoluciones_compra(db, nro_trans)


@router.get("/costos", response_model=schema_monitor.MonitorCosto)
def get_costos(
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
    return repository_monitor.get_costos(db, id_emp, bodega, negocio, categoria, subcategoria, page, size, articulos)


@router.get("/costos/export")
def exportar_costos(
    id_emp: int,
    bodega: int,
    negocio: int,
    categoria: int,
    subcategoria: int,
    articulos: List[int] = Query([]),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    filas = repository_monitor.get_costos_export_data(db, id_emp, bodega, negocio, categoria, subcategoria, articulos)
    buffer = repository_monitor.generar_excel_costos(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="costos.xlsx"'}
    )
