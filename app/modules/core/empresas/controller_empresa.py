from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_empresa, schema_empresa

router = APIRouter(
    prefix="/core/empresas",
    tags=["Core - Empresas"])

@router.get("/list", response_model=List[schema_empresa.EmpresaListaCombo])
def listar_empresas( db: Session = Depends(get_db)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresas(db)

@router.get("/listByNegocios", response_model=List[schema_empresa.EmpresaListaByNegocios])
def listar_empresas( db: Session = Depends(get_db)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresasByNegocios(db)