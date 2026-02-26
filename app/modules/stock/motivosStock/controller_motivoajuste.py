from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_motivoajuste ,schema_ajuste

router = APIRouter(
    prefix="/bodega/motivos",
    tags=["Bodega - Motivos"])

@router.get("/listCombo", response_model=List[schema_ajuste.MotivoCombo])
def listar_bodegas(db: Session = Depends(get_db)):
    """Obtiene la lista de todas los motivos."""
    return repository_motivoajuste.get_all(db)
