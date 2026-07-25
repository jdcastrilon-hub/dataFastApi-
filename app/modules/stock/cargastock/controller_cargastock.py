from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_cargastock, schema_cargastock
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/cargastock",
    tags=["Stock - Carga Masiva"])


@router.get("/plantilla")
def descargar_plantilla(
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    """Descarga un Excel en blanco con las columnas que espera la carga masiva."""
    buffer = repository_cargastock.generar_excel_plantilla()
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="plantilla_carga_inventario.xlsx"'}
    )


@router.post("/procesar")
def procesar_carga(
    idBodega: int = Form(...),
    idEstado: int = Form(...),
    idNegocio: int = Form(...),
    fechaMovimiento: str = Form(...),
    observacion: str = Form(None),
    confirmar: bool = Form(False),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    """Valida (confirmar=False) o valida+graba (confirmar=True) una carga masiva de
    inventario desde un archivo Excel. En ambos casos primero se valida el archivo
    completo; si hay errores no se graba nada, sin importar el valor de 'confirmar'.

    Nota: los campos del cabezal van sueltos (Form individuales) y no como un unico
    schema Pydantic porque FastAPI (0.129) no combina bien 'Annotated[Modelo, Form()]'
    con un UploadFile en el mismo endpoint (se probo y falla con 422 "Field required"
    incluso enviando los datos correctos) — es una limitacion real de esta version,
    no una decision de rendimiento."""
    contenido = archivo.file.read()
    fecha = datetime.fromisoformat(fechaMovimiento)

    resultado = repository_cargastock.procesar_carga_stock(
        db=db,
        id_bodega=idBodega,
        id_estado=idEstado,
        id_negocio=idNegocio,
        fecha_movimiento=fecha,
        observacion=observacion,
        nombre_archivo=archivo.filename,
        contenido=contenido,
        confirmar=confirmar,
        usuario_nombre=usuario_autenticado.usuario,
    )
    return resultado


@router.get("/pagination", response_model=schema_cargastock.PaginatedCargaStockResponse)
def list_cargas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_cargastock.get_cargas_paginated(db, page, size, texto)


@router.get("/search", response_model=schema_cargastock.CargaStockBase)
def obtener_carga(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una carga masiva específica x ID."""
    db_carga = repository_cargastock.get_carga_stock(db, id_trans=id_trans)
    if db_carga is None:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    return db_carga


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_carga(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una carga masiva del sistema (revierte su impacto en el stock/costos). No tiene edicion."""
    success = repository_cargastock.delete_carga_stock(db, id_trans=id_trans)
    if not success:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    return None
