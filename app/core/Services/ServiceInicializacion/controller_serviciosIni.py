from fastapi import APIRouter, FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from . import schema_serviciosIni , repository_serviciosIni

router = APIRouter(
    prefix="/core/services/ini",
    tags=["Core - Services"])

@router.get("/numerador/next", response_model=schema_serviciosIni.NumeradorResponse)
def listar_empresas(numerador : str,db: Session = Depends(get_db)):
    """Obtiene Numerador siguiente"""
    result =repository_serviciosIni.NumeradorNext(db,numerador)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"La secuencia '{numerador}' no existe en la base de datos."
        )
    return {"next_value": result["next_value"]}

#db: Session, id_articulo: int,id_codbarra: int, bodega_id: int, estado_id: int , id_proveedor : int
@router.get("/compraDisponiblexBodega", response_model=list[schema_serviciosIni.StockDisponibleResponse])
def get_compra_disponible(
    idArticulo: int ,
    idACodBarra: int ,
    idBodega: int ,
    idEstado: int ,
    idProveedor: int ,
    db: Session = Depends(get_db)
):
    return repository_serviciosIni.get_compra_disponible(db,idArticulo,idACodBarra, idBodega, idEstado,idProveedor) 