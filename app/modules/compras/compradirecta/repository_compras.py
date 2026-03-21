from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import models, schema_compras 
from app.modules.compras.proveedores import model_proveedor

#Paginacion
def get_compras_paginated(db: Session, page: int, size: int,idempresa: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(models.Compra).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = db.query(models.Compra)\
    .filter(models.Compra.id_emp == idempresa)\
    .options(
        joinedload(models.Compra.proveedor),
        joinedload(models.Compra.bodega))\
    .offset(offset)\
    .limit(size)\
    .all()
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


def create_compra(db: Session, obj: schema_compras.CompraCreate, nro_docum : int) :
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_compra = models.Compra(
            id_emp=obj.id_emp,
            id_proveedor=obj.id_proveedor,
            fec_doc =obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            remito= obj.remito,
            ingresa_bodega= obj.ingresa_bodega,
            id_bodega =obj.id_bodega,
            id_estado =obj.id_estado,
            imp_neto =obj.imp_neto,
            imp_descuento =obj.imp_descuento,
            imp_total =obj.imp_total,
            observaciones = obj.observacion,
            impuesto1 = obj.impuesto1,
            valor_impuesto1 = obj.valor_impuesto1,
            impuesto2 = obj.impuesto2,
            valor_impuesto2 = obj.valor_impuesto2,
            impuesto3 = obj.impuesto3,
            valor_impuesto3 = obj.valor_impuesto3,
            vista = obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_compra)
        db.flush() 

        # 2. Crear las subcategorías vinculadas
        for i,det in enumerate(obj.detalles, start=1):
            de_detalles = models.DetalleCompra(            
                id_trans = bd_compra.id_trans,            
                linea=i, #Numerador de linea
                #campos
                id_articulo = det.id_articulo,
                id_codbarra  = det.id_codbarra,
                ref_compras = det.ref_compras,
                costo_unit = det.costo_unit,
                cantidad  = det.cantidad,
                id_lote = det.id_lote,
                stock = det.stock,
                impuesto1 = det.impuesto1,
                id_tasaimp1 = det.id_tasaimp1,
                valor_impuesto1 = det.valor_impuesto1,
                impuesto2 = det.impuesto2,
                id_tasaimp2 = det.id_tasaimp2,
                valor_impuesto2 = det.valor_impuesto2,
                impuesto3 = det.impuesto3,
                id_tasaimp3 = det.id_tasaimp3,
                valor_impuesto3 = det.valor_impuesto3,
                costo_total = det.costo_total,
                importe = det.importe
            )
            db.add(de_detalles)
            

        # 3. Crear nuevos codigos de barra si es necesario
        for i,newcodigos in enumerate(obj.nuevoCodigoBarra, start=1):
            de_detalle_nuevoscodigos = models.DetalleCompraNuevoCodigoBarra( 
                id_trans = bd_compra.id_trans,
                id_articulo = newcodigos.id_articulo,
                id_codbarra = newcodigos.id_codbarra,
                linea=i, #Numerador de linea
                #Campos
                cod_barra = newcodigos.cod_barra,
                ref_barra=newcodigos.ref_barra
            )
            db.add(de_detalle_nuevoscodigos)
        
        db.flush() # Envio a base de datos

        # 3. LLAMAR AL STORED PROCEDURE (Antes del commit)
        # Usamos el ID que acabamos de generar
        db.execute(
            text("CALL public.sp_compradirecta(:operacion,:parm_trans)"), 
            {"operacion": "N", "parm_trans": bd_compra.id_trans}
        )   
        
        db.commit()
        db.refresh(bd_compra)
        return bd_compra

    except Exception as e:
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise HTTPException(status_code=400, detail=f"Error al crear la compra: {str(e)}")