from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_empresa, schema_empresa
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/empresas",
    tags=["Core - Empresas"])

@router.get("/list", response_model=List[schema_empresa.EmpresaListaCombo])
def listar_empresas( db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresas(db)

@router.get("/listByNegocios", response_model=List[schema_empresa.EmpresaListaByNegocios])
def listar_empresas( db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresasByNegocios(db)