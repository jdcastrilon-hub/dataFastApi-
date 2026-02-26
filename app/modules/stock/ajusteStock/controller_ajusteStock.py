from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_ajusteStock, schema_ajusteStock
from app.core.Services.ServiceInicializacion import repository_serviciosIni

router = APIRouter(
    prefix="/bodega/ajustestock",
    tags=["Stock - AjusteStock"])

@router.post("/save")
def crear_ajuste(ajustestock: schema_ajusteStock.AjusteStockCreate, db: Session = Depends(get_db)):
    """Crea una nueva bodega y retorna el objeto con su ID generado."""
    try:
        result=repository_serviciosIni.NumeradorNextReal(db,"id_nrodocum_ajustestock")
        print(result)
        repository_ajusteStock.create_ajustestock(db=db, obj=ajustestock, nro_docum=result)
        return {
            "status": "success",
            "message": "ajuste creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
        }
    except Exception as e:
        # Aquí devuelves un error controlado, por ejemplo 400 (Bad Request)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": f"Error al guardar: {str(e)}",
                "data": None
            }
        )