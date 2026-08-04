from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_estado ,schema_estado
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "INV_EST"

router = APIRouter(
    prefix="/bodega/estados",
    tags=["Stock - Estados"])

@router.get("/listCombo", response_model=List[schema_estado.EstadoCombo])
def listar_estados(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de todos los estados de la empresa activa."""
    return repository_estado.get_estados(db, id_emp=contexto.id_emp)

@router.get("/pagination", response_model=schema_estado.PaginatedEstadoResponse)
def list_estados_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_estado.get_estados_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_estado.EstadoResponse)
def obtener_estado(estado_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un estado específico x ID."""
    db_estado = repository_estado.get_estado(db, estado_id=estado_id)
    if db_estado is None or db_estado.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return db_estado

@router.post("/save")
def crear_estado(estado: schema_estado.EstadoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo estado y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codEstado duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    estado.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_estado.create_estado(db=db, obj=estado)
    return {
        "status": "success",
        "message": "Estado creado exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_estado(estado_id: int, estado: schema_estado.EstadoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de un estado existente (ver nota en crear_estado sobre el manejo de errores)."""
    db_estado = repository_estado.get_estado(db, estado_id=estado_id)
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    if db_estado.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    estado.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_estado.update_estado(db, estado_id=estado_id, obj=estado)
    return {
        "status": "success",
        "message": "Estado editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estado(estado_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un estado del sistema."""
    db_estado = repository_estado.get_estado(db, estado_id=estado_id)
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    if db_estado.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_estado.delete_estado(db, estado_id=estado_id)
    return None
