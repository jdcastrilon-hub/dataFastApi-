from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_cliente, schema_cliente
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/clientes",
    tags=["Comercial - Cliente"])

@router.get("/clientesearch", response_model=List[schema_cliente.ClienteSearch])
def search_articulos(
    query: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_cliente.find_clientes_by_query(db,query)

@router.post("/save")
def create_cliente(db_cliente: schema_cliente.ClienteCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo cliente y retorna el objeto con su ID generado."""
    repository_cliente.create_cliente(db=db, obj=db_cliente)
    return {
            "status": "success",
            "message": "Cliente creado exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }