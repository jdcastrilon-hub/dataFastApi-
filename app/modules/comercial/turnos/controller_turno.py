from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from . import squema_turno, repository_turno
from app.core.Services.ServiceInicializacion import repository_serviciosIni
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/turnos",
    tags=["comercial - turnos"])

@router.post("/save")
def crear_turno(turno: squema_turno.TurnoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva Caja"""
    result=repository_serviciosIni.NumeradorNextReal(db,"t_abrirturno_id_seq")
    print(result)
    repository_turno.create_turno(db=db, obj=turno,nro_docum=result)
    return {
            "status": "success",
            "message": "turno creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.get("/validacionturno", response_model=squema_turno.ValidacionTurno)
def search_turno(
    usuario: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_turno.validar_turnoxusuario(db,usuario)

@router.get("/ultimacajaxuser", response_model=squema_turno.UltimaCajaxuser)
def search_turno(
    usuario: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_turno.validar_ultimaCaja(db,usuario)