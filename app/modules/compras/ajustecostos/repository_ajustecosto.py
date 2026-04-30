from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import model_ajuste ,schema_ajustecosto

# Crear un ajuste de costos
def create_ajuste(db: Session, obj: schema_ajustecosto.AjusteBase):

     # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_ajuste = model_ajuste.AjusteCostoArticulo(
            linea=1,
            id_emp=obj.id_emp,
            fec_doc =obj.fec_doc,
            documento=obj.documento,
            id_bodega =obj.id_bodega,
            id_articulo=obj.id_articulo,
            observaciones=obj.observaciones,
            imp_costo_actual =obj.imp_costo_actual,
            imp_costo_nuevo =obj.imp_costo_nuevo,          
            vista = obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod)
        db.add(bd_ajuste)
        db.flush() 

        db.execute(
                text("CALL public.sp_ajustecostos(:operacion,:parm_trans)"), 
                {"operacion": "N", "parm_trans": bd_ajuste.id_trans}
            )   

        db.commit()
        db.refresh(bd_ajuste) 
        return bd_ajuste