from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_unidad ,schema_unidad

router = APIRouter(
    prefix="/bodega/unidades",
    tags=["Bodega - Unidades"])

@router.get("/list", response_model=List[schema_unidad.UnidadBase])
def listar_unidades(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las unidades."""
    return repository_unidad.get_unidades(db)