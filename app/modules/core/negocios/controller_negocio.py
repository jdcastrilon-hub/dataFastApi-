from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_negocios , schema_negocio
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/negocios",
    tags=["Core - Empresas"])

@router.get("/pagination", response_model=schema_negocio.PaginatedNegocioResponse)
def list_negocios_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_negocios.get_negocios_paginated(db, page, size, id_emp, texto)

@router.get("/search", response_model=schema_negocio.NegocioBase)
def obtener_negocio(
    id_negocio: int,
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un negocio especifico x ID, solo si pertenece a la empresa actual."""
    db_negocio = repository_negocios.get_negocio(db, id_negocio=id_negocio, id_emp=id_emp)
    if db_negocio is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return db_negocio

@router.post("/save")
def crear_negocio(negocio: schema_negocio.NegocioCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo negocio. No se atrapa la excepcion aqui a proposito: los errores
    de integridad (ej. codigo duplicado en la misma empresa) los resuelve el
    manejador global con un mensaje amigable."""
    repository_negocios.create_negocio(db=db, obj=negocio)
    return {
        "status": "success",
        "message": "Negocio creado exitosamente",
        "data": None
    }

@router.put("/edit/{id_negocio}")
def actualizar_negocio(id_negocio: int, id_emp: int, negocio: schema_negocio.NegocioCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita un negocio existente (ver nota en crear_negocio sobre el manejo de errores)."""
    db_actual = repository_negocios.update_negocio(db, id_negocio=id_negocio, id_emp=id_emp, obj=negocio)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return {
        "status": "success",
        "message": "Negocio editado exitosamente",
        "data": None
    }

@router.delete("/delete/{id_negocio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_negocio(id_negocio: int, id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un negocio del sistema."""
    success = repository_negocios.delete_negocio(db, id_negocio=id_negocio, id_emp=id_emp)
    if not success:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return None

@router.get("/listByNegocios", response_model=schema_negocio.NegocioxCategoriasDTO)
def listar_negocios_y_categorias(id_empresa: int,db: Session = Depends(get_db),  contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):

    data = repository_negocios.get_negocios_con_categorias_por_empresa(db,contexto.id_emp)
    
    if not data:
        # Devolver lista vacia , si no hay data
        return []
        
    return data

    