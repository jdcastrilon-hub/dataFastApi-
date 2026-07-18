from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from . import repository_cierreturno, schema_cierreturno

router = APIRouter(
    prefix="/comercial/cierreturno",
    tags=["Comercial - Cierre de Turno"])


@router.get("/pagination", response_model=schema_cierreturno.PaginatedCierreResponse)
def list_cierres_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_cierreturno.get_cierres_paginated(db, page, size, idempresa, texto)


@router.get("/resumen", response_model=schema_cierreturno.ResumenCierre)
def resumen_cierre(
    idTurno: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Agrupado de td_abrirturno (por concepto/medio de pago/signo) que alimenta
    la grilla del formulario de cierre - no persiste nada, es solo lectura."""
    return repository_cierreturno.get_resumen_cierre(db, id_turno=idTurno)


@router.get("/detalleconcepto", response_model=list[schema_cierreturno.DetalleConceptoLinea])
def detalle_concepto(
    idTurno: int,
    concepto: str,
    idMediopago: int,
    signo: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Nivel 2 del drill-down de cierre: facturas individuales detras de una
    fila agrupada de la grilla (mismo concepto/medio de pago/signo)."""
    return repository_cierreturno.get_detalle_concepto(db, id_turno=idTurno, concepto=concepto, id_mediopago=idMediopago, signo=signo)


@router.get("/search", response_model=schema_cierreturno.CierreTurnoBase)
def obtener_cierre(
    id: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    bd_cierre = repository_cierreturno.get_cierre_by_id(db, id=id)
    if bd_cierre is None:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    return bd_cierre


@router.post("/save")
def crear_cierre(
    cierre: schema_cierreturno.CierreTurnoCreate,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Cierra un turno: guarda cabecera+detalle ya agrupado (ver /resumen) y llama
    sp_comercial_cierreturno, que traslada el dinero a p_movimientocajas y marca
    t_abrirturno.status=false."""
    bd_cierre = repository_cierreturno.create_cierre(db=db, obj=cierre)
    return {
        "status": "success",
        "message": "Turno cerrado exitosamente",
        "data": {"idTrans": bd_cierre.id_trans}
    }
