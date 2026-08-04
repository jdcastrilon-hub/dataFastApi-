from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_listaprecio, repository_listaprecio
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "VEN_LISTA"

router = APIRouter(
    prefix="/comercial/listaprecio",
    tags=["Comercial - Lista de Precios"])


@router.get("/pagination", response_model=schema_listaprecio.PaginatedListaPrecioResponse)
def list_listaprecio_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_listaprecio.get_listaprecio_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/search", response_model=schema_listaprecio.ListaPrecioBase)
def obtener_listaprecio(id_lista: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca una lista de precios especifica por ID."""
    db_lista = repository_listaprecio.get_listaprecio_by_id(db, id_lista)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista de precios no encontrada")
    return db_lista


@router.post("/save")
def crear_listaprecio(lista: schema_listaprecio.ListaPrecioCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva lista de precios. No se atrapa la excepcion aqui a proposito:
    los errores de integridad (ej. ya existe una lista general) los resuelve el
    manejador global con un mensaje amigable."""
    lista.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_listaprecio.create_listaprecio(db=db, obj=lista)
    return {
        "status": "success",
        "message": "Lista de precios creada exitosamente",
        "data": None
    }


@router.put("/edit/{id_lista}")
def actualizar_listaprecio(id_lista: int, lista: schema_listaprecio.ListaPrecioCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza una lista de precios."""
    db_lista = repository_listaprecio.get_listaprecio_by_id(db, id_lista)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="La lista de precios no existe")
    if db_lista.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="La lista de precios no existe")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")
    repository_listaprecio.update_listaprecio(db, id_lista=id_lista, obj=lista)
    return {
        "status": "success",
        "message": "Lista de precios actualizada exitosamente",
        "data": None
    }


@router.delete("/delete/{id_lista}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_listaprecio(id_lista: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una lista de precios del sistema."""
    db_lista = repository_listaprecio.get_listaprecio_by_id(db, id_lista)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="La lista de precios no existe")
    if db_lista.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="La lista de precios no existe")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")
    repository_listaprecio.delete_listaprecio(db, id_lista=id_lista)
    return None
