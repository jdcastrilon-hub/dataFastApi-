from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
# Importación corregida:
from . import schemas, repository 

router = APIRouter(
    prefix="/paises", 
    tags=["Core - Países"]
)

@router.get("/", response_model=list[schemas.PaisResponse])
def listar_paises(db: Session = Depends(get_db)):
    return repository.get_paises(db)

@router.post("/", response_model=schemas.PaisResponse)
def guardar_pais(pais: schemas.PaisCreate, db: Session = Depends(get_db)):
    return repository.create_pais(db, pais)