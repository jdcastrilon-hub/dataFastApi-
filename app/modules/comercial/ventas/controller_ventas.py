from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repositoty_ventas, schema_ventas
from app.core.Services.ServiceInicializacion import repository_serviciosIni

router = APIRouter(
    prefix="/comercial/ventas",
    tags=["Comercial - Facturacion"])

@router.post("/save")
def create_cliente(bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente y retorna el objeto con su ID generado."""
    print(bd_factura.secuencia)
    result=repository_serviciosIni.NumeradorNextReal(db,bd_factura.secuencia)
    print(result)
    repositoty_ventas.create_venta(db=db, obj=bd_factura,nro_docum=result)
    return {
            "status": "success",
            "message": "Factura creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }