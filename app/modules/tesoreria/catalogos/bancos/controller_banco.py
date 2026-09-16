from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_banco, schema_banco
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "TES_BANCO"

router = APIRouter(
    prefix="/tesoreria/bancos",
    tags=["Tesoreria - Bancos"])

@router.get("/listCombo", response_model=list[schema_banco.BancoCombo])
def listar_bancos(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Bancos activos de la empresa actual (ej. seleccion en Medio de Pago)."""
    return repository_banco.get_bancos(db, id_emp=contexto.id_emp)

@router.get("/pagination", response_model=schema_banco.PaginatedBancoResponse)
def list_bancos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_banco.get_bancos_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_banco.BancoResponse)
def obtener_banco(banco_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un banco específico x ID."""
    db_banco = repository_banco.get_banco(db, banco_id=banco_id)
    if db_banco is None or db_banco.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    return db_banco

@router.post("/save")
def crear_banco(banco: schema_banco.BancoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo banco (ver nota en crear_estado sobre el manejo de errores:
    no se atrapa la excepcion aqui a proposito, el manejador global de
    IntegrityError la convierte en un mensaje amigable)."""
    banco.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_banco.create_banco(db=db, obj=banco)
    return {
        "status": "success",
        "message": "Banco creado exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_banco(banco_id: int, banco: schema_banco.BancoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de un banco existente."""
    db_banco = repository_banco.get_banco(db, banco_id=banco_id)
    if db_banco is None:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    if db_banco.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    banco.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_banco.update_banco(db, banco_id=banco_id, obj=banco)
    return {
        "status": "success",
        "message": "Banco editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_banco(banco_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un banco del sistema."""
    db_banco = repository_banco.get_banco(db, banco_id=banco_id)
    if db_banco is None:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    if db_banco.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_banco.delete_banco(db, banco_id=banco_id)
    return None
