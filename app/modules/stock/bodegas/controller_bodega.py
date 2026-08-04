from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_bodega, schema_bodega
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos). m_bodegas no tiene
# columna id_emp propia - se resuelve via bodega -> sucursal -> empresa
# (ver get_bodegas_paginated). El id_emp de estos endpoints tambien se usa
# para el chequeo de permiso.
MENU_CODIGO = "INV_BOD"

router = APIRouter(
    prefix="/bodega/bodegas",
    tags=["Stock - Bodegas"])
#Session = Depends(get_db) : Dependencia de base de datos
#""" = Documentacion del API

@router.get("/listCombo", response_model=List[schema_bodega.BodegaCombo])
def listar_bodegas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de bodegas de la empresa activa."""
    return repository_bodega.get_bodegas_combo(db, contexto.id_emp)


@router.get("/pagination", response_model=schema_bodega.PaginatedBodegaResponse)
def list_bodegas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_bodega.get_bodegas_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_bodega.BodegaResponse)
def obtener_bodega(bodega_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una bodega específica x ID."""
    db_bodega = repository_bodega.get_bodega(db, bodega_id=bodega_id)
    if db_bodega is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return db_bodega


@router.post("/save")
def crear_bodega(bodega: schema_bodega.BodegaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva bodega y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codBodega duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_bodega.create_bodega(db=db, bodega=bodega)
    return {
        "status": "success",
        "message": "Bodega creada exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_bodega(bodega_id: int, bodega: schema_bodega.BodegaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de una bodega existente (ver nota en crear_bodega sobre el manejo de errores)."""
    db_bodega = repository_bodega.get_bodega(db, bodega_id=bodega_id)
    if db_bodega is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    repository_bodega.update_bodega(db, bodega_id=bodega_id, bodega_data=bodega)
    return {
            "status": "success",
            "message": "Bodega editada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(bodega_id: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una bodega del sistema."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")
    success = repository_bodega.delete_bodega(db, bodega_id=bodega_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return None

@router.get("/stockDisponiblexBodega", response_model=List[schema_bodega.StockDisponibleResponse])
def get_stock_disponible(
    idArticulo: int ,
    idCodbarra: int ,
    idBodega: int ,
    idEstado: int ,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_bodega.get_stock_disponible(db,idArticulo,idCodbarra, idBodega, idEstado)

@router.get("/stockDisponibleMasivo", response_model=List[schema_bodega.StockDisponibleMasivoResponse])
def get_stock_disponible_masivo(
    idBodega: int,
    idEstado: int,
    cadena: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    """Recalcula el stock de varios codigos de barra (separados por '-') en una sola
    consulta, contra una bodega/estado puntual. Usado al cambiar de bodega/estado en
    una grilla que ya tiene articulos cargados (ajustestock/traslado)."""
    return repository_bodega.get_stock_disponible_masivo(db, idBodega, idEstado, cadena)