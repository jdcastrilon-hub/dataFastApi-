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
            forma_pago = obj.forma_pago,  
            imp_ingreso = obj.imp_ingreso,  
            imp_vuelto = obj.imp_vuelto,  
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

         # Insertar Detalles
        _procesar_detalles(db, bd_venta.id_trans,bd_venta.id_emp, obj)        
        db.flush() # Envio a base de datos

        
        db.commit()
        db.refresh(bd_venta)
        return bd_venta

    except Exception as e:
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise HTTPException(status_code=400, detail=f"Error al crear la venta: {str(e)}")
    



def _procesar_detalles(db: Session, id_trans: int,id_emp: str, obj: schema_ventas.ventaCreate):
        """
        Método privado para procesar e insertar detalles de venta
        Reutilizado en Creación y Edición.
        """
        for i,det in enumerate(obj.detalles, start=1):
            de_detalles = models_ventas.FacturaDetalle(     
                id_emp = id_emp,       
                id_trans = id_trans,            
                linea=i, #Numerador de linea
                #campos
                id_articulo = det.id_articulo,
                id_codbarra  = det.id_codbarra,
                precio_unit = det.precio_unit,
                cantidad  = det.cantidad,
                id_lote = det.id_lote,
                tipo_vta = "V",
                stock = det.stock,
                porc_dcto = det.porc_dcto,
                imp_dcto = det.imp_dcto,
                impuesto1 = det.impuesto1,
                id_tasaimp1 = det.id_tasaimp1,
                valor_impuesto1 = det.valor_impuesto1,
                impuesto2 = det.impuesto2,
                id_tasaimp2 = det.id_tasaimp2,
                valor_impuesto2 = det.valor_impuesto2,
                impuesto3 = det.impuesto3,
                id_tasaimp3 = det.id_tasaimp3,
                valor_impuesto3 = det.valor_impuesto3,
                imp_total = det.imp_total
            )
            db.add(de_detalles)