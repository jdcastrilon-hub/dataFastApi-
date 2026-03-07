from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_compras, schema_compras

router = APIRouter(
    prefix="/compras/compradirecta",
    tags=["Compras - Proveedor"])


@router.post("/save")
def crear_compra(ajustestock: schema_compras.CompraCreate, db: Session = Depends(get_db)):
    """Crea una nueva compra y retorna el objeto con su ID generado."""
    try:
        repository_compras.create_proveedor(db=db, obj=ajustestock)
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