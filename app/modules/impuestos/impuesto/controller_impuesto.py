from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_impuesto , schema_impuesto
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "COM_IMPUESTO"

router = APIRouter(
    prefix="/impuesto/tasas",
    tags=["Core - Impuesto"])

@router.get("/list", response_model=List[schema_impuesto.ImpuestoBase])
def lista_tasas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de todos los impuestos de la empresa (usado por el formulario de articulos)."""
    return repository_impuesto.get_impuestos(db, id_emp=contexto.id_emp)

@router.get("/listCombo", response_model=List[schema_impuesto.ImpuestoCombo])
def listar_tasas_combo(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de impuestos de la empresa para combos (compra-directa, venta-directa, venta-pos)."""
    return repository_impuesto.get_impuestos(db, id_emp=contexto.id_emp)

@router.get("/tipos/listCombo", response_model=List[schema_impuesto.TipoImpuestoCombo])
def listar_tipos_impuesto(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Catalogo global de tipos de impuesto (IVA, IVA2, ...) - no tiene CRUD propio."""
    return repository_impuesto.get_tipos_impuesto(db)

@router.get("/pagination", response_model=schema_impuesto.PaginatedImpuestoResponse)
def list_impuestos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_impuesto.get_impuestos_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_impuesto.ImpuestoResponse)
def obtener_impuesto(id_impuesto: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un impuesto especifico x ID."""
    db_impuesto = repository_impuesto.get_impuesto(db, id_impuesto=id_impuesto)
    if db_impuesto is None or db_impuesto.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Impuesto no encontrado")
    return db_impuesto

@router.post("/save")
def crear_impuesto(impuesto: schema_impuesto.ImpuestoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo impuesto y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así el manejador global de
    IntegrityError da un mensaje amigable si (tipoImpuesto, tasaImpuesto) ya existe."""
    impuesto.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_impuesto.create_impuesto(db=db, obj=impuesto)
    return {
        "status": "success",
        "message": "Impuesto creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_impuesto(id_impuesto: int, impuesto: schema_impuesto.ImpuestoCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de un impuesto existente."""
    db_impuesto = repository_impuesto.get_impuesto(db, id_impuesto=id_impuesto)
    if db_impuesto is None:
        raise HTTPException(status_code=404, detail="Impuesto no encontrado")
    if db_impuesto.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Impuesto no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    impuesto.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_impuesto.update_impuesto(db, id_impuesto=id_impuesto, obj=impuesto)
    return {
        "status": "success",
        "message": "Impuesto editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_impuesto(id_impuesto: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un impuesto del sistema."""
    db_impuesto = repository_impuesto.get_impuesto(db, id_impuesto=id_impuesto)
    if db_impuesto is None:
        raise HTTPException(status_code=404, detail="Impuesto no encontrado")
    if db_impuesto.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Impuesto no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_impuesto.delete_impuesto(db, id_impuesto=id_impuesto)
    return None
