from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_motivoajuste ,schema_ajuste
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/motivos",
    tags=["Bodega - Motivos"])

@router.get("/listCombo", response_model=List[schema_ajuste.MotivoCombo])
def listar_bodegas(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas los motivos."""
    return repository_motivoajuste.get_all(db)
