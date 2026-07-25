from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_trasladoStock, schema_trasladoStock
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "INV_TRAS"

router = APIRouter(
    prefix="/bodega/trasladobodega",
    tags=["Stock - Traslado"])

@router.get("/pagination", response_model=schema_trasladoStock.PaginatedTrasladoResponse)
def list_traslados_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_trasladoStock.get_traslados_paginated(db, page, size, texto)

@router.get("/search", response_model=schema_trasladoStock.TrasladoBase)
def obtener_traslado(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un traslado específico x ID."""
    db_traslado = repository_trasladoStock.get_trasladobodega(db, id_trans=id_trans)
    if db_traslado is None:
        raise HTTPException(status_code=404, detail="Traslado no encontrado")
    return db_traslado

@router.post("/save")
def crear_traslado(traslado: schema_trasladoStock.TrasladoStockCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo traslado entre bodegas y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    los resuelve el manejador global de IntegrityError con un mensaje amigable,
    en una sola llamada (el nroDocum también se asigna server-side, sin una
    llamada aparte al numerador)."""
    verificar_permiso(db, usuario_autenticado.id_usuario, traslado.id_emp, MENU_CODIGO, "CREAR")
    repository_trasladoStock.create_trasladobodega(db=db, obj=traslado)
    return {
        "status": "success",
        "message": "traslado creado exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_traslado(id_trans: int, traslado: schema_trasladoStock.TrasladoStockCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza un traslado existente (recalcula el impacto en el stock de origen y destino)."""
    verificar_permiso(db, usuario_autenticado.id_usuario, traslado.id_emp, MENU_CODIGO, "EDITAR")
    db_traslado = repository_trasladoStock.update_trasladobodega(db, id_trans=id_trans, obj=traslado)
    if db_traslado is None:
        raise HTTPException(status_code=404, detail="Traslado no encontrado")
    return {
        "status": "success",
        "message": "Traslado editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_traslado(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un traslado del sistema (revierte su impacto en el stock)."""
    db_traslado = repository_trasladoStock.get_trasladobodega(db, id_trans=id_trans)
    if db_traslado is None:
        raise HTTPException(status_code=404, detail="Traslado no encontrado")
    verificar_permiso(db, usuario_autenticado.id_usuario, db_traslado.id_emp, MENU_CODIGO, "ELIMINAR")

    success = repository_trasladoStock.delete_trasladobodega(db, id_trans=id_trans)
    if not success:
        raise HTTPException(status_code=404, detail="Traslado no encontrado")
    return None
