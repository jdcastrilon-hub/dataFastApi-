from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_estado ,schema_estado

router = APIRouter(
    prefix="/bodega/estados",
    tags=["Bodega - Motivos"])

@router.get("/listCombo", response_model=List[schema_estado.EstadoCombo])
def listar_estados(db: Session = Depends(get_db)):
    """Obtiene la lista de todas los motivos."""
    return repository_estado.get_estados(db)
