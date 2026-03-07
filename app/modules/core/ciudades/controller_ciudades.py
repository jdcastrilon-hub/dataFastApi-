from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_ciudades ,schema_ciudades

router = APIRouter(
    prefix="/core/ciudad",
    tags=["Bodega - Costeo"])

@router.get("/listCombo", response_model=List[schema_ciudades.CiudadCombo])
def listar_Costeo(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las ciudades."""
    return repository_ciudades.get_ciudades(db)