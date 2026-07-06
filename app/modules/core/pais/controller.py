from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
# Importación corregida:
from . import schemas, repository
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/paises",
    tags=["Core - Países"]
)

@router.get("/", response_model=list[schemas.PaisResponse])
def listar_paises(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository.get_paises(db)

@router.post("/", response_model=schemas.PaisResponse)
def guardar_pais(pais: schemas.PaisCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository.create_pais(db, pais)