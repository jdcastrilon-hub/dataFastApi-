from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from . import squema_turno, repository_turno

router = APIRouter(
    prefix="/comercial/turnos",
    tags=["comercial - turnos"])

@router.post("/save")
def crear_turno(turno: squema_turno.TurnoCreate, db: Session = Depends(get_db)):
    """Crea una nueva Caja"""
    repository_turno.create_turno(db=db, obj=turno)
    return {
            "status": "success",
            "message": "turno creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }
  
@router.get("/validacionturno", response_model=squema_turno.ValidacionTurno)
def search_turno(
    usuario: str,
    db: Session = Depends(get_db)):
    return repository_turno.validar_turnoxusuario(db,usuario)