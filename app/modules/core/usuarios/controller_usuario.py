from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_usuario, esquema_usuario
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/usuarios",
    tags=["Core - usuario"])

@router.get("/pagination", response_model=esquema_usuario.PaginatedUsuarioResponse)
def list_usuarios_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_usuario.get_usuario_paginated(db, page, size, id_emp, texto)

@router.get("/search", response_model=List[esquema_usuario.UsuarioSearch])
def usuario_search(
    query: str,
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Autocompletar (combo-usuario: asignacion en roles/sucursales/cajas/conceptos,
    etc), acotado a los usuarios de la empresa actual. No confundir con /detalle,
    que es la busqueda por id usada por la pantalla de edicion."""
    return repository_usuario.find_usuarios_by_query(db, query, id_emp)

@router.get("/detalle", response_model=esquema_usuario.UsuarioResponse)
def obtener_usuario(
    usuario_id: int,
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un usuario especifico x ID, solo si pertenece a la empresa actual."""
    db_usuario = repository_usuario.get_usuario(db, usuario_id=usuario_id, id_emp=id_emp)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.post("/save")
def create_usuario(db_usuario: esquema_usuario.UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo usuario (y lo asocia a la empresa actual via md_empresaxuser).
    No se atrapa la excepcion aqui a proposito: asi los errores de integridad
    (ej. usuario o documento duplicado) los resuelve el manejador global de
    IntegrityError con un mensaje amigable, en una sola llamada."""
    repository_usuario.create_usuario(db=db, obj=db_usuario)
    return {
        "status": "success",
        "message": "Usuario creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_usuario(usuario_id: int, id_emp: int, db_usuario: esquema_usuario.UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza los datos propios de un usuario existente (ver nota en create_usuario sobre el manejo de errores)."""
    db_actual = repository_usuario.get_usuario(db, usuario_id=usuario_id, id_emp=id_emp)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    repository_usuario.update_usuario(db, usuario_id=usuario_id, obj=db_usuario)
    return {
        "status": "success",
        "message": "Usuario editado exitosamente",
        "data": None
    }
