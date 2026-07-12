from sqlalchemy import cast, desc, or_, String, text
from sqlalchemy.orm import Session, joinedload
from . import models, schema_ajusteStock
from app.modules.stock.bodegas import model_bodega
from app.modules.core.sucursales import model_sucursal
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de nroDocum
CODIGO_NUMERADOR_AJUSTESTOCK = "AJUSTESTOCK"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_id_emp_de_bodega(db: Session, id_bodega: int):
    """Resuelve la empresa dueña de la bodega: Bodega -> Sucursal -> id_emp."""
    resultado = (
        db.query(model_sucursal.Sucursal.id_emp)
        .join(model_bodega.Bodega, model_bodega.Bodega.id_sucursal == model_sucursal.Sucursal.id)
        .filter(model_bodega.Bodega.id == id_bodega)
        .first()
    )
    return resultado[0] if resultado else None

def _siguiente_nro_docum(db: Session, id_bodega: int, nro_docum_manual):
    """Asigna el nroDocum desde el numerador de la empresa dueña de la bodega.
    Si esa empresa tiene "requiere_consecutivo" en False, respeta lo enviado."""
    id_emp = _obtener_id_emp_de_bodega(db, id_bodega)
    if id_emp is None:
        return nro_docum_manual

    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_AJUSTESTOCK)
    return siguiente if siguiente is not None else nro_docum_manual

#Paginacion
def get_ajustes_paginated(db: Session, page: int, size: int, texto: str = None):
    query = db.query(models.AjusteStock)

    # Filtro de busqueda por numero de documento u observacion (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                cast(models.AjusteStock.nro_docum, String).ilike(patron),
                models.AjusteStock.observacion.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = (
    query
    .options(
        joinedload(models.AjusteStock.bodega),
        joinedload(models.AjusteStock.estado),
        joinedload(models.AjusteStock.motivo))\
    .order_by(desc(models.AjusteStock.fecha_mod))
    .offset(offset)
    .limit(size)
    .all()
)

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Obtener un ajuste por ID
def get_ajustestock(db: Session, id_trans: int):
    return db.query(models.AjusteStock).filter(models.AjusteStock.id_trans == id_trans)\
                    .options(joinedload(models.AjusteStock.detalles)
                    .joinedload(models.DetalleAjusteStock.articulo)).first()

def create_ajustestock(db: Session, obj: schema_ajusteStock.AjusteStockCreate):
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        nro_docum = _siguiente_nro_docum(db, obj.id_bodega, obj.nro_docum)

        # 1. Crear el objeto principal
        bd_cabecera = models.AjusteStock(
            id_emp=obj.id_emp,
            id_bodega=obj.id_bodega,
            documento=obj.documento,
            nro_docum=nro_docum,
            id_calculo=obj.id_calculo,
            fecha_movimiento=obj.fecha_movimiento,
            id_estado=obj.id_estado,
            id_motivo=obj.id_motivo,
            observacion=obj.observacion,
            vista=obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_cabecera)
        db.flush() # Envio a base de datos

        # 2. Crear las lineas de detalle vinculadas
        for i,sub in enumerate(obj.detalles, start=1):
            db_sub = models.DetalleAjusteStock(
                id_trans=bd_cabecera.id_trans,
                id_articulo=sub.id_articulo,
                id_codbarra=sub.id_codbarra,
                linea=i, #Numerador de linea
                id_ubicacion=sub.id_ubicacion,
                id_lote=sub.id_lote,
                cant_disp=sub.cant_disp,
                cantidad=sub.cantidad
            )
            db.add(db_sub)

        # 2b. Staging de lotes nuevos: aun no existen en m_lotes, el SP los crea
        # como parte del mismo commit (ver sp_stock_impacto_ajustestock).
        for i, lote in enumerate(obj.nuevos_lotes, start=1):
            db.add(models.DetalleAjusteStockNuevoLote(
                id_trans=bd_cabecera.id_trans,
                id_articulo=lote.id_articulo,
                id_lote=lote.id_lote,
                linea=i,
                codigo_lote=lote.codigo_lote,
                fec_vencimiento=lote.fec_vencimiento
            ))

        db.flush() # Envio a base de datos

        # 3. LLAMAR AL STORED PROCEDURE (Antes del commit)
        # Usamos el ID que acabamos de generar
        db.execute(
            text("CALL public.sp_stock_impacto_AjusteStock(:operacion,:parm_trans)"),
            {"operacion": "N", "parm_trans": bd_cabecera.id_trans}
        )

        db.commit()
        db.refresh(bd_cabecera)

        return bd_cabecera

    except Exception:
        db.rollback()
        raise

# Actualizar un ajuste existente
def update_ajustestock(db: Session, id_trans: int, obj: schema_ajusteStock.AjusteStockCreate):
    bd_cabecera = db.query(models.AjusteStock).filter(models.AjusteStock.id_trans == id_trans).first()
    if not bd_cabecera:
        return None

    try:
        # 1. Actualizamos los campos de la cabecera (el nroDocum ya asignado NO se toca)
        bd_cabecera.id_emp = obj.id_emp
        bd_cabecera.id_bodega = obj.id_bodega
        bd_cabecera.id_calculo = obj.id_calculo
        bd_cabecera.fecha_movimiento = obj.fecha_movimiento
        bd_cabecera.id_estado = obj.id_estado
        bd_cabecera.id_motivo = obj.id_motivo
        bd_cabecera.observacion = obj.observacion
        bd_cabecera.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        bd_cabecera.fecha_mod = obj.fecha_mod

        # 2. Reemplazamos las lineas de detalle
        db.query(models.DetalleAjusteStock).filter(models.DetalleAjusteStock.id_trans == id_trans).delete()
        db.query(models.DetalleAjusteStockNuevoLote).filter(models.DetalleAjusteStockNuevoLote.id_trans == id_trans).delete()
        db.flush()

        for i, sub in enumerate(obj.detalles, start=1):
            db_sub = models.DetalleAjusteStock(
                id_trans=id_trans,
                id_articulo=sub.id_articulo,
                id_codbarra=sub.id_codbarra,
                linea=i,
                id_ubicacion=sub.id_ubicacion,
                id_lote=sub.id_lote,
                cant_disp=sub.cant_disp,
                cantidad=sub.cantidad
            )
            db.add(db_sub)

        for i, lote in enumerate(obj.nuevos_lotes, start=1):
            db.add(models.DetalleAjusteStockNuevoLote(
                id_trans=id_trans,
                id_articulo=lote.id_articulo,
                id_lote=lote.id_lote,
                linea=i,
                codigo_lote=lote.codigo_lote,
                fec_vencimiento=lote.fec_vencimiento
            ))
        db.flush()

        # 3. Volvemos a llamar al SP: borra e inserta de nuevo el impacto en p_stock
        # a partir de la cabecera/detalle ya actualizados.
        db.execute(
            text("CALL public.sp_stock_impacto_AjusteStock(:operacion,:parm_trans)"),
            {"operacion": "E", "parm_trans": id_trans}
        )

        db.commit()
        db.refresh(bd_cabecera)
        return bd_cabecera

    except Exception:
        db.rollback()
        raise

# Eliminar un ajuste (revierte también su impacto en el stock)
def delete_ajustestock(db: Session, id_trans: int):
    bd_cabecera = db.query(models.AjusteStock).filter(models.AjusteStock.id_trans == id_trans).first()
    if not bd_cabecera:
        return None

    try:
        # 1. Revertimos el impacto que este ajuste dejó en el stock
        db.execute(text("DELETE FROM p_stock WHERE id_trans = :id_trans"), {"id_trans": id_trans})

        # 2. Borramos el detalle, el staging de lotes nuevos (si quedo alguno) y la cabecera
        db.query(models.DetalleAjusteStock).filter(models.DetalleAjusteStock.id_trans == id_trans).delete()
        db.query(models.DetalleAjusteStockNuevoLote).filter(models.DetalleAjusteStockNuevoLote.id_trans == id_trans).delete()
        db.delete(bd_cabecera)

        db.commit()
        return bd_cabecera

    except Exception:
        db.rollback()
        raise
