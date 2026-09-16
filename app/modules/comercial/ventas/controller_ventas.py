from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repositoty_ventas, schema_ventas
from app.core.numeradores import repository_numerador
from app.modules.comercial.documentos import repository_docum
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/ventas",
    tags=["Comercial - Facturacion"])

#Buscar venta por ID
@router.get("/search", response_model=schema_ventas.VentaBase)
def obtener_venta(id_trans: int, id_emp: int = 1, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una venta específica x ID."""
    bd_venta = repositoty_ventas.get_venta_by_id(db, id_trans=id_trans, id_emp=id_emp)
    if bd_venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return bd_venta

@router.get("/stock-precio-masivo", response_model=List[schema_ventas.VentaActualizacionDatos])
def get_stock_precio_masivo(cadena: str, id_bodega: int, id_estado: int, id_lista: int = 0, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Recalcula stock y precio de varios articulos en una sola consulta - usado
    cuando cambia bodega/estado/lista de precios con lineas ya cargadas en la grilla."""
    return repositoty_ventas.consultar_stock_precio_lote(db, cadena, id_bodega, id_estado, id_lista)


@router.get("/pagination", response_model=schema_ventas.PaginatedVentaResponse)
def list_ventas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    vista: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repositoty_ventas.get_ventas_paginated(db, page, size, idempresa, texto, vista)

@router.post("/save")
def create_venta_directa(bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db)):
    """Crea una nueva venta directa y retorna el objeto con su ID generado.
    Usa el numerador por empresa (md_numeradores), igual que compradirecta/ajustestock/
    trasladobodega/savepos. El codigo del numerador es bd_factura.secuencia (el mismo valor que antes
    identificaba la secuencia nativa de Postgres del documento en m_documventas),
    no un codigo fijo - asi cada documento (Contado/Credito/etc) mantiene su propio
    consecutivo independiente en vez de compartir uno solo por empresa."""
    result = repository_numerador.siguiente_numerador(db, bd_factura.id_emp, bd_factura.secuencia)
    if result is None:
        # La empresa no requiere consecutivo: respeta lo que envio el formulario
        result = bd_factura.nro_docum
    repositoty_ventas.create_venta(db=db, obj=bd_factura,nro_docum=result)
    return {
            "status": "success",
            "message": "Factura creada exitosamente",
            "data": bd_factura  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit/{id_trans}")
def actualizar_venta(id_trans: int, bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Editar una venta (ver nota en repositoty_ventas.update_venta sobre el alcance/limitacion conocida)."""
    repositoty_ventas.update_venta(db=db, id_trans=id_trans, id_emp=bd_factura.id_emp, obj=bd_factura)
    return {
        "status": "success",
        "message": "Venta editada exitosamente",
        "data": None
    }

@router.post("/savepos")
def create_venta_pos(bd_factura: schema_ventas.ventaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
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

    # 4. Obtener el siguiente numero via md_numeradores (mismo mecanismo por-empresa
    # que ya usa /save para venta-directa) - antes usaba NumeradorNextReal (nextval()
    # nativo de Postgres sobre m_documventas), dejado asi deliberadamente cuando se
    # migro /save; ahora se alinea tambien.
    result = repository_numerador.siguiente_numerador(db, bd_factura.id_emp, bd_factura.secuencia)
    if result is None:
        # La empresa no requiere consecutivo: respeta lo que envio el formulario
        result = bd_factura.nro_docum
    print(f"Numerador generado: {result}")
    bd_factura.nro_docum = result
    
    # 5. Crear la venta en el repositorio
    repositoty_ventas.create_venta(db=db, obj=bd_factura, nro_docum=result)
    
    return {
        "status": "success",
        "message": "Factura creada exitosamente",
        "data": bd_factura  # Omites el objeto completo para ahorrar recursos
    }