from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import respository_medio, schema_medio
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/mediopago",
    tags=["Comercial - MedioPago"])

@router.get("/list", response_model=List[schema_medio.MedioPagoCombo])
def search_medios_pago(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return respository_medio.get_medios_pago(db)
