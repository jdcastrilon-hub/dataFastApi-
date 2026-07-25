from datetime import date

from fastapi import APIRouter, Depends, Query
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
