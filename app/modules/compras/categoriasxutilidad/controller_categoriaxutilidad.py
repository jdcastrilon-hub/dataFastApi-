from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_categoriaxutilidad, schema_categoriaxutilidad
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "COM_UTILCAT"

router = APIRouter(
    prefix="/compras/categoriasxutilidad",
    tags=["Compras - Utilidad x Categoria"])


@router.get("/pagination", response_model=schema_categoriaxutilidad.PaginatedCategoriaXUtilidadResponse)
def list_categoriaxutilidad_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_categoriaxutilidad.get_categoriaxutilidad_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/search", response_model=schema_categoriaxutilidad.CategoriaXUtilidadResponse)
def obtener_categoriaxutilidad(id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca una fila especifica x ID."""
    db_obj = repository_categoriaxutilidad.get_categoriaxutilidad(db, id)
    if db_obj is None or db_obj.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Configuración de utilidad no encontrada")
    return db_obj


@router.post("/save")
def crear_categoriaxutilidad(obj: schema_categoriaxutilidad.CategoriaXUtilidadCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva fila de utilidad x categoria/subcategoria.
    No se atrapa la excepción aquí a propósito: si ya existe una fila para la
    misma categoria (o subcategoria), el manejador global de IntegrityError
    responde con el mensaje amigable del indice unico parcial."""
    obj.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_categoriaxutilidad.create_categoriaxutilidad(db=db, obj=obj)
    return {
        "status": "success",
        "message": "Configuración de utilidad creada exitosamente",
        "data": None
    }


@router.put("/edit/{id}")
def actualizar_categoriaxutilidad(id: int, obj: schema_categoriaxutilidad.CategoriaXUtilidadCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza una fila existente de utilidad x categoria/subcategoria."""
    db_obj = repository_categoriaxutilidad.get_categoriaxutilidad(db, id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Configuración de utilidad no encontrada")
    if db_obj.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Configuración de utilidad no encontrada")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    obj.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_categoriaxutilidad.update_categoriaxutilidad(db, id=id, obj=obj)
    return {
        "status": "success",
        "message": "Configuración de utilidad editada exitosamente",
        "data": None
    }


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoriaxutilidad(id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una fila de utilidad x categoria/subcategoria."""
    db_obj = repository_categoriaxutilidad.get_categoriaxutilidad(db, id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Configuración de utilidad no encontrada")
    if db_obj.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Configuración de utilidad no encontrada")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_categoriaxutilidad.delete_categoriaxutilidad(db, id=id)
    return None
