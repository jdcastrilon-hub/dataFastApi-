from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_personas, schema_personas
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/personas",
    tags=["compras - Personas"])


@router.get("/list", response_model=List[schema_personas.PersonaBase])
def listar_documentos(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todos los tipos de documentos."""
    return repository_personas.get_personas(db)

@router.get("/personaSearch", response_model=List[schema_personas.PersonaSearch])
def search_articulos(
    query: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_personas.find_persona_by_query(db,query)

@router.get("/search", response_model=schema_personas.PersonaDetalle)
def obtener_persona(
    id_persona: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Trae el detalle completo de una persona (usado para cargar sus datos al seleccionarla)."""
    persona = repository_personas.get_persona(db, id_persona=id_persona)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona