from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from . import repository_movcaja, schema_movcaja

router = APIRouter(
    prefix="/comercial/movimientocaja",
    tags=["Comercial - Movimiento Caja"])


@router.get("/pagination", response_model=schema_movcaja.PaginatedMovCajaResponse)
def list_movcajas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_movcaja.get_movcajas_paginated(db, page, size, idempresa, texto)


@router.get("/search", response_model=schema_movcaja.MovCajaBase)
def obtener_movcaja(
    id: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un movimiento de caja especifico x ID. No hay edicion/borrado para
    este modulo (registro contable, solo crear y consultar)."""
    bd_mov = repository_movcaja.get_movcaja_by_id(db, id=id)
    if bd_mov is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return bd_mov


@router.post("/save")
def crear_movcaja(
    mov: schema_movcaja.MovCajaCreate,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un movimiento de caja (ingreso/gasto manual) - impacta el cuadre del
    turno via sp_comercial_movcaja (inserta en td_abrirturno como Efectivo)."""
    bd_mov = repository_movcaja.create_movcaja(db=db, obj=mov)
    return {
        "status": "success",
        "message": "Movimiento de caja creado exitosamente",
        "data": {"id": bd_mov.id}
    }
