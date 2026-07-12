from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_proveedor, schema_proveedor
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/proveedor",
    tags=["Compras - Proveedor"])

@router.get("/pagination", response_model=schema_proveedor.PaginatedProveedorResponse)
def list_bodegas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_proveedor.get_proveedor_paginated(db, page, size, texto)

@router.get("/proveedorsearch", response_model=List[schema_proveedor.ProveedorSearch])
def search_articulos(
    query: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_proveedor.find_proveedores_by_query(db,query)

@router.get("/search", response_model=schema_proveedor.ProveedorResponse)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un proveedor específico x ID, con su persona asociada."""
    db_proveedor = repository_proveedor.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return db_proveedor

@router.post("/save")
def create_proveedor(db_proveedor: schema_proveedor.ProveedorCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo proveedor y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codigoTitular duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    repository_proveedor.create_proveedor(db=db, obj=db_proveedor)
    return {
        "status": "success",
        "message": "Proveedor creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_proveedor(proveedor_id: int, db_proveedor: schema_proveedor.ProveedorCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza los datos propios de un proveedor existente (ver nota en create_proveedor sobre el manejo de errores)."""
    db_actual = repository_proveedor.get_proveedor(db, proveedor_id=proveedor_id)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    repository_proveedor.update_proveedor(db, proveedor_id=proveedor_id, obj=db_proveedor)
    return {
        "status": "success",
        "message": "Proveedor editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un proveedor del sistema."""
    success = repository_proveedor.delete_proveedor(db, proveedor_id=proveedor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return None