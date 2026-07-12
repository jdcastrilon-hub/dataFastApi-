from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_unidad ,schema_unidad
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/unidades",
    tags=["Bodega - Unidades"])

@router.get("/list", response_model=List[schema_unidad.UnidadCombo])
def listar_unidades(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las unidades."""
    return repository_unidad.get_unidades(db)

@router.get("/pagination", response_model=schema_unidad.PaginatedUnidadResponse)
def list_unidades_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_unidad.get_unidades_paginated(db, page, size, texto)

@router.get("/search", response_model=schema_unidad.UnidadResponse)
def obtener_unidad(unidad_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una unidad específica x ID."""
    db_unidad = repository_unidad.get_unidad(db, unidad_id=unidad_id)
    if db_unidad is None:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return db_unidad

@router.post("/save")
def crear_unidad(unidad: schema_unidad.UnidadCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva unidad y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codUnidad duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    repository_unidad.create_unidad(db=db, obj=unidad)
    return {
        "status": "success",
        "message": "Unidad creada exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_unidad(unidad_id: int, unidad: schema_unidad.UnidadCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza los datos de una unidad existente (ver nota en crear_unidad sobre el manejo de errores)."""
    db_unidad = repository_unidad.get_unidad(db, unidad_id=unidad_id)
    if db_unidad is None:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    repository_unidad.update_unidad(db, unidad_id=unidad_id, obj=unidad)
    return {
        "status": "success",
        "message": "Unidad editada exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_unidad(unidad_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una unidad del sistema."""
    success = repository_unidad.delete_unidad(db, unidad_id=unidad_id)
    if not success:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return None
