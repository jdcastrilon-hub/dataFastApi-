from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_ajusteStock, schema_ajusteStock
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "INV_AJU"

router = APIRouter(
    prefix="/bodega/ajustestock",
    tags=["Stock - AjusteStock"])

@router.get("/pagination", response_model=schema_ajusteStock.PaginatedAjusteResponse)
def list_bodegas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_ajusteStock.get_ajustes_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_ajusteStock.AjusteStockBase)
def obtener_bodega(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un ajuste específica x ID."""
    db_ajuste = repository_ajusteStock.get_ajustestock(db, id_trans=id_trans)
    if db_ajuste is None:
        raise HTTPException(status_code=404, detail="ajuste no encontrada")
    return db_ajuste

@router.post("/save")
def crear_ajuste(ajustestock: schema_ajusteStock.AjusteStockCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo ajuste de stock y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    los resuelve el manejador global de IntegrityError con un mensaje amigable,
    en una sola llamada (el nroDocum también se asigna server-side, sin una
    llamada aparte al numerador)."""
    ajustestock.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_ajusteStock.create_ajustestock(db=db, obj=ajustestock)
    return {
        "status": "success",
        "message": "ajuste creada exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_ajuste(id_trans: int, ajustestock: schema_ajusteStock.AjusteStockCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza un ajuste de stock existente (recalcula el impacto en el stock)."""
    db_ajuste = repository_ajusteStock.get_ajustestock(db, id_trans=id_trans)
    if db_ajuste is None:
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    if db_ajuste.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    ajustestock.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    db_ajuste = repository_ajusteStock.update_ajustestock(db, id_trans=id_trans, obj=ajustestock)
    if db_ajuste is None:
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    return {
        "status": "success",
        "message": "Ajuste editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ajuste(id_trans: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un ajuste de stock del sistema (revierte su impacto en el stock)."""
    db_ajuste = repository_ajusteStock.get_ajustestock(db, id_trans=id_trans)
    if db_ajuste is None:
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    if db_ajuste.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    success = repository_ajusteStock.delete_ajustestock(db, id_trans=id_trans)
    if not success:
        raise HTTPException(status_code=404, detail="Ajuste no encontrado")
    return None
