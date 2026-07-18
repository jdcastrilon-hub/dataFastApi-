from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_docum, repository_docum
from app.core.Services.ServiceInicializacion import repository_serviciosIni
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/documentos",
    tags=["comercial - documentos"])

@router.get("/pagination", response_model=schema_docum.PaginatedDocumVentasResponse)
def list_documentos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_docum.get_documentos_paginated(db, page, size, idempresa, texto)

#Buscar documento de venta por su llave compuesta
@router.get("/search", response_model=schema_docum.MDocumVentasBase)
def obtener_documento(
    id_emp: int,
    id_sucursal_emp: int,
    documento: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un documento de venta especifico por (idEmp, idSucursal, documento)."""
    bd_documento = repository_docum.get_documento_by_key(db, id_emp=id_emp, id_sucursal_emp=id_sucursal_emp, documento=documento)
    if bd_documento is None:
        raise HTTPException(status_code=404, detail="Documento de venta no encontrado")
    return bd_documento

@router.post("/save")
def crear_documento(documento: schema_docum.MDocumVentasCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo documento de venta. No se atrapa la excepcion aqui a proposito:
    un documento duplicado para la misma empresa/sucursal (llave compuesta ya
    duplicada) lo resuelve el manejador global de IntegrityError con un mensaje
    amigable, sin endpoint de validacion previa."""
    repository_docum.create_documento(db=db, obj=documento)
    return {
            "status": "success",
            "message": "Documento de venta creado exitosamente",
            "data": None
    }

@router.put("/edit")
def actualizar_documento(
    id_emp: int,
    id_sucursal_emp: int,
    documento: str,
    obj: schema_docum.MDocumVentasCreate,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita un documento de venta existente (identificado por su llave compuesta original)."""
    db_documento = repository_docum.update_documento(db, id_emp=id_emp, id_sucursal_emp=id_sucursal_emp, documento=documento, obj=obj)
    if db_documento is None:
        raise HTTPException(status_code=404, detail="Documento de venta no encontrado")
    return {
        "status": "success",
        "message": "Documento de venta editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_documento(
    id_emp: int,
    id_sucursal_emp: int,
    documento: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un documento de venta del sistema."""
    success = repository_docum.delete_documento(db, id_emp=id_emp, id_sucursal_emp=id_sucursal_emp, documento=documento)
    if not success:
        raise HTTPException(status_code=404, detail="Documento de venta no encontrado")
    return None
