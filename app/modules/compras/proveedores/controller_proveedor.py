from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_proveedor, schema_proveedor
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
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_proveedor.get_proveedor_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/proveedorsearch", response_model=List[schema_proveedor.ProveedorSearch])
def search_articulos(
    query: str,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_proveedor.find_proveedores_by_query(db, contexto.id_emp, query)

@router.get("/search", response_model=schema_proveedor.ProveedorResponse)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un proveedor específico x ID, con su persona asociada."""
    db_proveedor = repository_proveedor.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None or db_proveedor.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return db_proveedor

@router.post("/save")
def create_proveedor(db_proveedor: schema_proveedor.ProveedorCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo proveedor y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codigoTitular duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    db_proveedor.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_proveedor.create_proveedor(db=db, obj=db_proveedor)
    return {
        "status": "success",
        "message": "Proveedor creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_proveedor(proveedor_id: int, db_proveedor: schema_proveedor.ProveedorCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos propios de un proveedor existente (ver nota en create_proveedor sobre el manejo de errores)."""
    db_actual = repository_proveedor.get_proveedor(db, proveedor_id=proveedor_id)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    if db_actual.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db_proveedor.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_proveedor.update_proveedor(db, proveedor_id=proveedor_id, obj=db_proveedor)
    return {
        "status": "success",
        "message": "Proveedor editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un proveedor del sistema."""
    db_actual = repository_proveedor.get_proveedor(db, proveedor_id=proveedor_id)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    repository_proveedor.delete_proveedor(db, proveedor_id=proveedor_id)
    return None