from sqlalchemy import text
from sqlalchemy.orm import Session
from . import model_ajusteprecio, schema_ajusteprecio


# Crea un ajuste de precio (encabezado auditable) e impacta p_precios con un
# INSERT directo - a diferencia de ajustecosto, no hace falta un stored
# procedure: p_precios ya tiene sus propios triggers (ins_p_precios /
# ins_p_precios_reglas, ver alembic 9c8225580f88) que actualizan el snapshot
# s_precioxarticulo y cascadean las reglas de categoria solo con la fila
# insertada - mismo mecanismo que ya usa repository_cargastock.py.
def create_ajuste(db: Session, obj: schema_ajusteprecio.AjustePrecioBase):
    logs_dict = [log.model_dump() for log in obj.logs]

    bd_ajuste = model_ajusteprecio.AjustePrecioLista(
        linea=1,
        id_emp=obj.id_emp,
        id_lista=obj.id_lista,
        fec_doc=obj.fec_doc,
        documento=obj.documento,
        id_articulo=obj.id_articulo,
        observaciones=obj.observaciones,
        imp_precio_actual=obj.imp_precio_actual,
        imp_precio_nuevo=obj.imp_precio_nuevo,
        vista=obj.vista,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(bd_ajuste)
    db.flush()

    usuario_mod = logs_dict[-1].get('usuario_mod') if logs_dict else None

    db.execute(
        text("""
            INSERT INTO public.p_precios (id_trans, linea, id_emp, id_lista, id_articulo,
                precio_anterior, precio_nuevo, origen, usuario_mod, fecha_mod)
            VALUES (:id_trans, 1, :id_emp, :id_lista, :id_articulo,
                :precio_anterior, :precio_nuevo, 'MANUAL', :usuario, :fecha_mod)
        """),
        {
            "id_trans": bd_ajuste.id_trans,
            "id_emp": obj.id_emp,
            "id_lista": obj.id_lista,
            "id_articulo": obj.id_articulo,
            "precio_anterior": obj.imp_precio_actual,
            "precio_nuevo": obj.imp_precio_nuevo,
            "usuario": usuario_mod,
            "fecha_mod": obj.fecha_mod
        }
    )

    db.commit()
    db.refresh(bd_ajuste)
    return bd_ajuste
