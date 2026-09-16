from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from . import repository_monitor, schema_monitor
from app.core.auth import security

router = APIRouter(
    prefix="/tesoreria/monitor",
    tags=["Tesoreria - Monitor"])


@router.get("/filtros", response_model=schema_monitor.FiltrosTesoreria)
def filtros(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_monitor.get_filtros(db, contexto.id_emp)


@router.get("/movimientos", response_model=schema_monitor.MonitorTesoreria)
def get_movimientos(
    fecha_inicial: Optional[date] = None,
    fecha_final: Optional[date] = None,
    tipo_cuenta: str = Query("TODAS"),
    id_caja: Optional[int] = None,
    id_banco: Optional[int] = None,
    id_mediopago: Optional[int] = None,
    vista: Optional[str] = None,
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)
):
    return repository_monitor.get_movimientos(
        db, contexto.id_emp, fecha_inicial, fecha_final, tipo_cuenta,
        id_caja, id_banco, id_mediopago, vista, page, size
    )


@router.get("/movimientos/export")
def exportar_movimientos(
    fecha_inicial: Optional[date] = None,
    fecha_final: Optional[date] = None,
    tipo_cuenta: str = Query("TODAS"),
    id_caja: Optional[int] = None,
    id_banco: Optional[int] = None,
    id_mediopago: Optional[int] = None,
    vista: Optional[str] = None,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)
):
    filas = repository_monitor.get_movimientos_export_data(
        db, contexto.id_emp, fecha_inicial, fecha_final, tipo_cuenta,
        id_caja, id_banco, id_mediopago, vista
    )
    buffer = repository_monitor.generar_excel_movimientos(filas)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="movimientos_tesoreria.xlsx"'}
    )
