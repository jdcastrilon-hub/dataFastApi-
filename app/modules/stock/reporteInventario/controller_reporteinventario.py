from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import schema_reporteinventario , repository_reporteinventario
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/stock/reporteinventario",
    tags=["Stock - Reporte"])

@router.get("/inventarioBodega", response_model=List[schema_reporteinventario.EmpresaListaByNegocios])
def listar_negocios_y_categorias(id_empresa: int,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):

    data = repository_reporteinventario.get_empresa_by_negocios_sucursales(db)

    if not data:
        # Devolver lista vacia , si no hay data
        return []

    return data

@router.get("/inventario", response_model=schema_reporteinventario.PaginatedInventarioResponse)
def listar_inventario(page: int = Query(0, ge=0),
                      size: int = Query(10, ge=1),
                      bodega_id: int =0,
                      db: Session = Depends(get_db),
                      usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    # Aquí podrías agregar lógica de skip/limit si necesitas paginar de verdad
    print(bodega_id)
    return repository_reporteinventario.get_inventario_por_bodega(db, bodega_id,page,size)