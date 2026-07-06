from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_impuesto , schema_impuesto
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/impuesto/tasas",
    tags=["Core - Impuesto"])

@router.get("/list", response_model=List[schema_impuesto.ImpuestoBase])
def lista_tasas(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas los impuestos."""
    return repository_impuesto.get_impuestos(db)

@router.get("/listCombo", response_model=List[schema_impuesto.ImpuestoCombo])
def listar_tasas_combo(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las bodegas."""
    return repository_impuesto.get_impuestos(db)