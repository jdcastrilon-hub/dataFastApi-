from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_categoria, repository_categoria
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "INV_CAT"

router = APIRouter(
    prefix="/bodega/categorias",
    tags=["Stock - Categorias"])

@router.get("/pagination", response_model=schema_categoria.PaginatedBodegaResponse)
def list_categorias_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_categoria.get_categorias_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_categoria.CategoriaBase)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una categoria específica x ID."""
    db_categoria= repository_categoria.get_categoriaByID(db, categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return db_categoria

@router.post("/save")
def crear_categoria(categoria: schema_categoria.CategoriaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva categoria"""
    categoria.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_categoria.create_categoria(db=db, cat=categoria)
    return {
            "status": "success",
            "message": "Categoria creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }


@router.put("/edit/{id_categoria}")
def actualizar_categoria(id_categoria: int, categoria: schema_categoria.CategoriaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de una categoria """
    db_categoria = repository_categoria.get_categoriaByID(db, id_categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="La categoria no existe")
    if db_categoria.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="La categoria no existe")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")
    repository_categoria.update_categoria(db, id_categoria=id_categoria, obj=categoria)
    return {
                "status": "success",
                "message": "Categoria actualizado exitosamente",
                "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.delete("/delete/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una categoria del sistema."""
    db_categoria = repository_categoria.get_categoriaByID(db, id_categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="La categoria no existe")
    if db_categoria.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="La categoria no existe")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_categoria.delete_categoria(db, id_categoria=id_categoria)
    return None