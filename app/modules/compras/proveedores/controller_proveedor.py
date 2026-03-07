from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_proveedor, schema_proveedor

router = APIRouter(
    prefix="/compras/proveedor",
    tags=["Compras - Proveedor"])

@router.get("/proveedorsearch", response_model=List[schema_proveedor.ProveedorSearch])
def search_articulos(
    query: str, 
    db: Session = Depends(get_db)):
    return repository_proveedor.find_proveedores_by_query(db,query)

@router.post("/save")
def create_proveedor(db_proveedor: schema_proveedor.ProveedorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo proveedor y retorna el objeto con su ID generado."""
    try:
        repository_proveedor.create_proveedor(db=db, obj=db_proveedor)
        return {
            "status": "success",
            "message": "proveedor creado exitosamente",
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