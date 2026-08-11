from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_cargaprecios, schema_cargaprecios
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/cargaprecios",
    tags=["Comercial - Carga de Precios"])


@router.get("/plantilla")
def descargar_plantilla(
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)
):
    """Descarga un Excel en blanco con las columnas que espera la carga de precios."""
    buffer = repository_cargaprecios.generar_excel_plantilla()
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="plantilla_carga_precios.xlsx"'}
    )


@router.post("/procesar")
def procesar_carga(
    idLista: int = Form(...),
    fechaCarga: str = Form(...),
    observacion: str = Form(None),
    confirmar: bool = Form(False),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)
):
    """Valida (confirmar=False) o valida+graba (confirmar=True) una carga masiva de
    precios desde un archivo Excel. En ambos casos primero se valida el archivo
    completo; si hay errores no se graba nada, sin importar 'confirmar'."""
    contenido = archivo.file.read()
    fecha = datetime.fromisoformat(fechaCarga)

    resultado = repository_cargaprecios.procesar_carga_precios(
        db=db,
        id_lista=idLista,
        fecha_carga=fecha,
        observacion=observacion,
        nombre_archivo=archivo.filename,
        contenido=contenido,
        confirmar=confirmar,
        usuario_nombre=contexto.usuario.usuario,
        id_emp=contexto.id_emp,
    )
    return resultado


@router.get("/pagination", response_model=schema_cargaprecios.PaginatedCargaPreciosResponse)
def list_cargas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_cargaprecios.get_cargas_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/search", response_model=schema_cargaprecios.CargaPreciosBase)
def obtener_carga(id_trans: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca una carga de precios especifica x ID."""
    db_carga = repository_cargaprecios.get_carga_precios(db, id_trans=id_trans)
    if db_carga is None or db_carga.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    return db_carga

# No hay edicion ni eliminacion a proposito - ver nota en repository_cargaprecios.py.
