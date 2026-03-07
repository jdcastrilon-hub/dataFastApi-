from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_documentos, schema_documentos

router = APIRouter(
    prefix="/compras/tipodoc",
    tags=["compras - TipoDocumentos"])


@router.get("/listCombo", response_model=List[schema_documentos.TipoDocCombo])
def listar_documentos(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los tipos de documentos."""
    return repository_documentos.get_documentos(db)