from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
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

        # El SP no recibe el usuario de un contexto de sesion (Python solo lo llama con
        # operacion/parm_trans): se toma del ultimo log, mismo criterio ya usado para
        # p_costos.usuario_mod en sp_compradirecta/sp_compras_devoluciones.
        usuario_mod = logs_dict[-1].get('usuario_mod') if logs_dict else None
        db.execute(
                text("CALL public.sp_ajustecostos(:operacion,:parm_trans,:usuario)"),
                {"operacion": "N", "parm_trans": bd_ajuste.id_trans, "usuario": usuario_mod}
            )

        db.commit()
        db.refresh(bd_ajuste)
        return bd_ajuste