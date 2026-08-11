from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_cliente, schema_cliente
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "VEN_CLI"

router = APIRouter(
    prefix="/comercial/clientes",
    tags=["Comercial - Cliente"])


@router.get("/pagination", response_model=schema_cliente.PaginatedClienteResponse)
def list_clientes_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_cliente.get_cliente_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/clientesearch", response_model=List[schema_cliente.ClienteSearch])
def search_clientes(
    query: str,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_cliente.find_clientes_by_query(db, contexto.id_emp, query)


@router.get("/search", response_model=schema_cliente.ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un cliente especifico x ID, con su persona asociada."""
    db_cliente = repository_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None or db_cliente.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente


@router.post("/save")
def create_cliente(db_cliente: schema_cliente.ClienteCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo cliente. No se atrapa la excepcion aqui a proposito: los
    errores de integridad (ej. codigoTitular duplicado) los resuelve el
    manejador global con un mensaje amigable, en una sola llamada."""
    db_cliente.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_cliente.create_cliente(db=db, obj=db_cliente)
    return {
        "status": "success",
        "message": "Cliente creado exitosamente",
        "data": None
    }


@router.put("/edit")
def actualizar_cliente(cliente_id: int, db_cliente: schema_cliente.ClienteCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos propios de un cliente existente."""
    db_actual = repository_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    db_cliente.id_emp = contexto.id_emp
    repository_cliente.update_cliente(db, cliente_id=cliente_id, obj=db_cliente)
    return {
        "status": "success",
        "message": "Cliente editado exitosamente",
        "data": None
    }


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un cliente del sistema."""
    db_actual = repository_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_cliente.delete_cliente(db, cliente_id=cliente_id)
    return None
