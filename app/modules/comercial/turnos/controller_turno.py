from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from . import squema_turno, repository_turno
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/turnos",
    tags=["comercial - turnos"])

#Buscar turno por ID
@router.get("/search", response_model=squema_turno.TurnoBase)
def obtener_turno(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un turno específico x ID."""
    bd_turno = repository_turno.get_turno_by_id(db, id=id)
    if bd_turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return bd_turno

@router.get("/pagination", response_model=squema_turno.PaginatedTurnoResponse)
def list_turnos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_turno.get_turnos_paginated(db, page, size, idempresa, usuario_autenticado.usuario, texto)

@router.post("/save")
def crear_turno(turno: squema_turno.TurnoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo turno (apertura de caja). El numero de turno usa el
    numerador por empresa (md_numeradores, codigo 'TURNO'), ver repository_turno."""
    repository_turno.create_turno(db=db, obj=turno)
    return {
            "status": "success",
            "message": "turno creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit/{id}")
def actualizar_turno(id: int, turno: squema_turno.TurnoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Editar un turno (no incluye cierre de turno, ver nota en repository_turno.update_turno)."""
    repository_turno.update_turno(db=db, id=id, obj=turno)
    return {
        "status": "success",
        "message": "Turno editado exitosamente",
        "data": None
    }

@router.get("/validacionturno", response_model=squema_turno.ValidacionTurno)
def validar_turno(
    usuario: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_turno.validar_turnoxusuario(db,usuario)

@router.get("/ultimacajaxuser", response_model=squema_turno.UltimaCajaxuser)
def obtener_ultima_caja(
    usuario: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_turno.validar_ultimaCaja(db,usuario)