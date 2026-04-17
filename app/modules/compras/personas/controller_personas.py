from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_personas, schema_personas

router = APIRouter(
    prefix="/compras/personas",
    tags=["compras - Personas"])


@router.get("/list", response_model=List[schema_personas.PersonaBase])
def listar_documentos(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los tipos de documentos."""
    return repository_personas.get_personas(db)

@router.get("/personaSearch", response_model=List[schema_personas.PersonaSearch])
def search_articulos(
    query: str, 
    db: Session = Depends(get_db)):
    return repository_personas.find_persona_by_query(db,query)