from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.exceptions import TransaccionValidationError
from app.modules.compras.proveedores import model_proveedor
from app.core.numeradores import repository_numerador
from . import models, schema_devolucion

# Codigo del numerador (por empresa) que identifica el consecutivo de nroDocum
CODIGO_NUMERADOR_DEVOLUCION = "DEVOLUCION"

def _siguiente_nro_docum(db: Session, id_emp: int, nro_docum_manual):
    """Asigna el nroDocum desde el numerador de la empresa. Si esa empresa tiene
    "requiere_consecutivo" en False, respeta lo enviado desde el formulario."""
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_DEVOLUCION)
    return siguiente if siguiente is not None else nro_docum_manual

#Paginacion
def get_devoluciones_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(models.DevolucionCompra).filter(models.DevolucionCompra.id_emp == id_emp)

    # Filtro de busqueda por numero de devolucion o nombre del proveedor
    if texto:
        patron = f"%{texto}%"
        query = query\
            .join(models.DevolucionCompra.proveedor)\
            .filter(
                or_(
                    cast(models.DevolucionCompra.nro_docum, String).ilike(patron),
                    model_proveedor.Proveedor.razon_social.ilike(patron)
                )
            )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(
            joinedload(models.DevolucionCompra.proveedor),
            joinedload(models.DevolucionCompra.compra_origen))\
        .order_by(desc(models.DevolucionCompra.fecha_mod))\
        .offset(offset)\
        .limit(size)\
        .all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Compras Finalizadas de un proveedor, candidatas a ser la "compra origen" de una
# devolucion. Un Borrador nunca impacto stock, no hay nada que devolver de ahi.
# texto filtra por numero de documento o remito (alimenta el autocompletar del
# frontend, para que un proveedor con muchas compras sea buscable en vez de listarlas
# todas de una vez).
def get_compras_origen_by_proveedor(db: Session, id_proveedor: int, texto: str = None):
    condicion_texto = ""
    params = {"id_proveedor": id_proveedor}
    if texto:
        condicion_texto = "AND (CAST(nro_docum AS TEXT) ILIKE :texto OR remito ILIKE :texto)"
        params["texto"] = f"%{texto}%"

    return db.execute(
        text(f"""
            SELECT id_trans, nro_docum, remito, fec_doc, imp_total
            FROM t_compras
            WHERE id_proveedor = :id_proveedor AND status = 'F'
            {condicion_texto}
            ORDER BY fec_doc DESC
            LIMIT 20
        """),
        params
    ).mappings().all()

# Lineas de la compra origen, anotadas con el stock disponible ACTUAL (respeta el
# lote de cada linea si el articulo lo maneja) - alimenta la modal de seleccion.
# "cantidad_comprada" ya viene NETA de lo devuelto en devoluciones previas de esta
# misma compra origen (para que una compra pueda tener varias devoluciones sin
# permitir devolver de nuevo lo que ya se devolvio). excluir_id_trans se usa al
# editar una devolucion existente, para no restarse a si misma de ese acumulado.
def get_lineas_disponibles(db: Session, id_compra_origen: int, excluir_id_trans: int = None):
    return db.execute(
        text("""
            SELECT
                B.linea,
                B.id_articulo,
                B.id_codbarra,
                B.id_lote,
                COALESCE(M.codigo_lote, '') AS cod_lote,
                COALESCE(C.cod_barra, '') AS cod_articulo,
                COALESCE(C.ref_barra, B.ref_compras) AS nom_articulo,
                COALESCE(D.maneja_lote, false) AS maneja_lote,
                (B.cantidad - COALESCE(DEV.ya_devuelta, 0)) AS cantidad_comprada,
                B.costo_unit,
                CASE
                    WHEN B.id_lote > 0 THEN COALESCE(L.cantidad, 0)
                    ELSE COALESCE(S.cantidad, 0)
                END AS stock_disponible
            FROM td_compras B
            INNER JOIN t_compras A ON A.id_trans = B.id_trans
            LEFT JOIN m_artxcodigobarra C ON C.id_articulo = B.id_articulo AND C.id_codbarra = B.id_codbarra
            LEFT JOIN m_articulos D ON D.id_articulo = B.id_articulo
            LEFT JOIN m_lotes M ON M.id = B.id_lote
            LEFT JOIN s_stkbodegas S ON S.id_bodega = A.id_bodega AND S.id_estado = A.id_estado
                AND S.id_articulo = B.id_articulo AND S.id_codbarra = B.id_codbarra
            LEFT JOIN s_stkbodegaxlote L ON L.id_bodega = A.id_bodega AND L.id_estado = A.id_estado
                AND L.id_articulo = B.id_articulo AND L.id_lote = B.id_lote
            LEFT JOIN (
                SELECT TD.id_articulo, TD.id_codbarra, TD.id_lote, SUM(TD.cantidad) AS ya_devuelta
                FROM td_devolucioncompras TD
                INNER JOIN t_devolucioncompras T ON T.id_trans = TD.id_trans
                WHERE T.id_compra_origen = :id_compra_origen
                    AND (:excluir_id_trans IS NULL OR TD.id_trans != :excluir_id_trans)
                GROUP BY TD.id_articulo, TD.id_codbarra, TD.id_lote
            ) DEV ON DEV.id_articulo = B.id_articulo AND DEV.id_codbarra = B.id_codbarra AND DEV.id_lote = B.id_lote
            WHERE B.id_trans = :id_compra_origen
            ORDER BY B.linea
        """),
        {"id_compra_origen": id_compra_origen, "excluir_id_trans": excluir_id_trans}
    ).mappings().all()

# Obtener una devolucion por ID
def get_devolucion_by_id(db: Session, id_trans: int):
    devolucion = db.query(models.DevolucionCompra).filter(models.DevolucionCompra.id_trans == id_trans).options(
                    joinedload(models.DevolucionCompra.proveedor),
                    joinedload(models.DevolucionCompra.bodega),
                    joinedload(models.DevolucionCompra.compra_origen),
                    joinedload(models.DevolucionCompra.motivo),
                    joinedload(models.DevolucionCompra.detalles)
                    .joinedload(models.DetalleDevolucionCompra.articulo)).first()

    if devolucion is not None:
        _anotar_cod_lote_y_cantidad_comprada(db, devolucion)

    return devolucion

# El detalle guardado (td_devolucioncompras) no conserva el codigo de lote ni la
# cantidad originalmente comprada: se recalculan aqui a partir de m_lotes/td_compras
# solo para mostrarlos en el formulario de ver/editar (no son columnas propias).
def _anotar_cod_lote_y_cantidad_comprada(db: Session, devolucion):
    for det in devolucion.detalles:
        det.cod_lote = ""
        if det.id_lote > 0:
            lote = db.execute(
                text("SELECT codigo_lote FROM m_lotes WHERE id = :id_lote"),
                {"id_lote": det.id_lote}
            ).mappings().first()
            det.cod_lote = lote["codigo_lote"] if lote else ""

        original = db.execute(
            text("""
                SELECT cantidad FROM td_compras
                WHERE id_trans = :id_compra_origen AND id_articulo = :id_articulo
                    AND id_codbarra = :id_codbarra AND id_lote = :id_lote
            """),
            {
                "id_compra_origen": devolucion.id_compra_origen,
                "id_articulo": det.id_articulo,
                "id_codbarra": det.id_codbarra,
                "id_lote": det.id_lote
            }
        ).mappings().first()
        det.cantidad_comprada = original["cantidad"] if original else 0

#Crear devolucion. No maneja Borrador/Finalizado: impacta stock/costos de una vez al guardar.
def create_devolucion(db: Session, obj: schema_devolucion.DevolucionCompraCreate):
    try:
        logs_dict = [log.model_dump() for log in obj.logs]
        nro_docum = _siguiente_nro_docum(db, obj.id_emp, obj.nro_docum)

        bd_devolucion = models.DevolucionCompra(
            id_emp=obj.id_emp,
            id_sucursal=obj.id_sucursal,
            id_proveedor=obj.id_proveedor,
            id_compra_origen=obj.id_compra_origen,
            id_bodega=obj.id_bodega,
            id_estado=obj.id_estado,
            fec_doc=obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            id_motivo=obj.id_motivo,
            observacion=obj.observacion,
            status=obj.status or 'R',  # 'R' = Registrada; reservado, sin logica todavia
            imp_total=obj.imp_total,
            vista=obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_devolucion)
        db.flush()

        _procesar_detalles(db, bd_devolucion.id_trans, obj)
        db.flush()

        # Impacta p_stock/p_costos de inmediato (no hay Borrador/Finalizado aqui).
        db.execute(
            text("CALL public.sp_compras_devoluciones(:operacion, :parm_trans)"),
            {"operacion": "N", "parm_trans": bd_devolucion.id_trans}
        )

        db.commit()
        db.refresh(bd_devolucion)
        return bd_devolucion

    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))

# Actualizar una devolucion existente
def update_devolucion(db: Session, id_trans: int, obj: schema_devolucion.DevolucionCompraCreate):
    try:
        bd_devolucion = db.query(models.DevolucionCompra).filter(models.DevolucionCompra.id_trans == id_trans).first()
        if not bd_devolucion:
            return None

        bd_devolucion.id_proveedor = obj.id_proveedor
        bd_devolucion.id_compra_origen = obj.id_compra_origen
        bd_devolucion.id_bodega = obj.id_bodega
        bd_devolucion.id_estado = obj.id_estado
        bd_devolucion.fec_doc = obj.fec_doc
        bd_devolucion.id_motivo = obj.id_motivo
        bd_devolucion.observacion = obj.observacion
        bd_devolucion.imp_total = obj.imp_total
        bd_devolucion.logs = [log.model_dump() for log in obj.logs]
        bd_devolucion.fecha_mod = obj.fecha_mod

        db.query(models.DetalleDevolucionCompra).filter(models.DetalleDevolucionCompra.id_trans == id_trans).delete()
        db.flush()

        _procesar_detalles(db, id_trans, obj)
        db.flush()

        # Vuelve a llamar al SP: borra e inserta de nuevo el impacto en p_stock/p_costos
        # a partir de la cabecera/detalle ya actualizados.
        db.execute(
            text("CALL public.sp_compras_devoluciones(:operacion, :parm_trans)"),
            {"operacion": "E", "parm_trans": id_trans}
        )

        db.commit()
        db.refresh(bd_devolucion)
        return bd_devolucion

    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))

# Eliminar una devolucion (revierte su impacto en p_stock/p_costos)
def delete_devolucion(db: Session, id_trans: int):
    bd_devolucion = db.query(models.DevolucionCompra).filter(models.DevolucionCompra.id_trans == id_trans).first()
    if not bd_devolucion:
        return None

    try:
        db.execute(text("DELETE FROM public.p_stock WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})
        db.execute(text("DELETE FROM public.p_costos WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})

        db.delete(bd_devolucion)  # cascade borra el detalle (td_devolucioncompras)
        db.commit()
        return bd_devolucion
    except Exception:
        db.rollback()
        raise

def _procesar_detalles(db: Session, id_trans: int, obj: schema_devolucion.DevolucionCompraCreate):
    for i, det in enumerate(obj.detalles, start=1):
        db.add(models.DetalleDevolucionCompra(
            id_trans=id_trans,
            linea=i,
            id_articulo=det.id_articulo,
            id_codbarra=det.id_codbarra,
            id_lote=det.id_lote,
            cantidad=det.cantidad,
            costo_unit=det.costo_unit,
            costo_total=det.costo_total
        ))
