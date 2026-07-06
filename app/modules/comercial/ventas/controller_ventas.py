from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repositoty_ventas, schema_ventas
from app.core.Services.ServiceInicializacion import repository_serviciosIni
from app.modules.comercial.documentos import repository_docum
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/ventas",
    tags=["Comercial - Facturacion"])

@router.post("/save")
def create_cliente(bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
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

@router.post("/savepos")
def create_cliente(bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una venta/factura actualizando serie y secuencia desde el documento."""
    
    # 1. Buscar el documento base en la base de datos
    docum = repository_docum.consulta_x_documento(
        db, bd_factura.id_emp, bd_factura.id_sucursal_emp, bd_factura.documento
    )
    
    # 2. Validación crucial: Si no existe el documento, lanzar un 404
    if not docum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró el documento '{bd_factura.documento}' para la empresa y sucursal especificadas."
        )
    
    # 3. Asignar los campos vacíos de bd_factura con los datos de la BD
    # Nota: Asegúrate de que 'serie_docum' y 'secuencia' existan en tu modelo 'docum'
    bd_factura.serie_docum = docum.serie_docum
    bd_factura.secuencia = docum.secuencia  
    
    print(f"Secuencia actualizada: {bd_factura.secuencia}")
    
    # 4. Obtener el siguiente número real del numerador utilizando la secuencia actualizada
    result = repository_serviciosIni.NumeradorNextReal(db, bd_factura.secuencia)
    print(f"Numerador generado: {result}")
    bd_factura.nro_docum = result
    
    # 5. Crear la venta en el repositorio
    repositoty_ventas.create_venta(db=db, obj=bd_factura, nro_docum=result)
    
    return {
        "status": "success",
        "message": "Factura creada exitosamente",
        "data": bd_factura  # Omites el objeto completo para ahorrar recursos
    }