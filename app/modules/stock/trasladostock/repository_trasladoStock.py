from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from . import models, schema_trasladoStock 

def create_ajustestock(db: Session, obj: schema_trasladoStock.TrasladoStockCreate, nro_docum: int):
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_cabecera = models.TrasladoStock(
            id_bodega_origen=obj.id_bodega_origen,
            id_bodega_destino=obj.id_bodega_destino,
            documento=obj.documento,
            nro_docum=nro_docum,
            id_calculo=obj.id_calculo,
            fecha_movimiento=obj.fecha_movimiento,
            id_estado_origen=obj.id_estado_origen,
            id_estado_destino=obj.id_estado_destino,
            observacion=obj.observacion,
            vista=obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_cabecera)
        db.flush() # Envio a base de datos

        # 2. Crear los detalles
        for i,sub in enumerate(obj.detalles, start=1):
            db_sub = models.DetalleTrasladoStock(
                id_trans=bd_cabecera.id_trans,
                id_articulo=sub.id_articulo,
                linea=i, #Numerador de linea
                id_ubicacion=sub.id_ubicacion,
                id_lote=sub.id_lote,
                cant_disp=sub.cant_disp,
                cantidad=sub.cantidad
            )
            db.add(db_sub)
            
        db.flush() # Envio a base de datos

        # 3. LLAMAR AL STORED PROCEDURE (Antes del commit)
        # Usamos el ID que acabamos de generar
        db.execute(
            text("CALL public.sp_stock_impacto_trasladobodega(:operacion,:parm_trans)"), 
            {"operacion": "N", "parm_trans": bd_cabecera.id_trans}
        )   

        db.commit()
        db.refresh(bd_cabecera)

        return bd_cabecera
    
    except Exception as e:
            db.rollback() 
            raise e      