from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_personas, schema_personas
from app.core.auth import security

router = APIRouter(
    prefix="/compras/personas",
    tags=["compras - Personas"])


@router.get("/personaSearch", response_model=List[schema_personas.PersonaSearch])
def search_articulos(
    query: str,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_personas.find_persona_by_query(db, contexto.id_emp, query)

@router.get("/pagination", response_model=schema_personas.PaginatedPersonaResponse)
def list_personas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(100, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Listado para el modal "Seleccionar persona" (Proveedores/Clientes): top de
    la empresa activa, filtrable por documento o nombre."""
    return repository_personas.get_personas_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_personas.PersonaDetalle)
def obtener_persona(
    id_persona: int,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Trae el detalle completo de una persona (usado para cargar sus datos al seleccionarla)."""
    persona = repository_personas.get_persona(db, id_persona=id_persona)
    if persona is None or persona.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona
