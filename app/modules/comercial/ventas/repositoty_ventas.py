from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import models_ventas, schema_ventas 


#Crear venta
def create_venta(db: Session, obj: schema_ventas.ventaCreate, nro_docum : int) :
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_venta = models_ventas.Factura(
            id_emp=obj.id_emp,
            id_cliente=obj.id_cliente,
            id_sucursal_cliente=1,
            id_sucursal_emp=obj.id_sucursal_emp,
            id_bodega =obj.id_bodega,

            fec_doc =obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            serie_docum=obj.serie_docum,

            documento_ref="",            
            nro_ref=0,            
            serie_ref="",              
            documento_remito="",            
            nro_remito=0,            
            serie_remito="",     

            observacion = obj.observacion,     
            id_pago=1,
            fec_venc= obj.fec_doc,   
            id_moneda=1,       
            id_estado =obj.id_estado,
            vista = obj.vista,
            signo=1,

            imp_neto =obj.imp_neto,
            porc_dcto= obj.porc_dcto,
            imp_descuento =obj.imp_descuento,
            imp_total =obj.imp_total,
            
            impuesto1 = obj.impuesto1,
            valor_impuesto1 = obj.valor_impuesto1,
            impuesto2 = obj.impuesto2,
            valor_impuesto2 = obj.valor_impuesto2,
            impuesto3 = obj.impuesto3,
            valor_impuesto3 = obj.valor_impuesto3,
            
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_venta)
        db.flush() 

        
        db.commit()
        db.refresh(bd_venta)
        return bd_venta

    except Exception as e:
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise HTTPException(status_code=400, detail=f"Error al crear la venta: {str(e)}")
    