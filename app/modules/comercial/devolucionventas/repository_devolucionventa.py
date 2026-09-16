from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.exceptions import TransaccionValidationError
from app.modules.comercial.clientes import model_cliente
from app.modules.comercial.documentos import model_docum
from app.core.numeradores import repository_numerador
from . import model_devolucionventa as models, schema_devolucionventa as schema_devolucion


def _siguiente_nro_docum(db: Session, id_emp: int, id_sucursal: int, documento: str, nro_docum_manual):
    """Asigna el nroDocum desde el numerador real del documento elegido (md_numeradores,
    llave = m_documventas.secuencia = "documento-codSucursal", igual que venta-directa/POS
    - ver repository_docum.py::_calcular_secuencia). Si esa empresa tiene
    "requiere_consecutivo" en False, respeta lo enviado desde el formulario."""
    secuencia = db.query(model_docum.DocumentoVenta.secuencia).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal,
        model_docum.DocumentoVenta.documento == documento
    ).scalar()
    if not secuencia:
        raise TransaccionValidationError(
            f"No existe el documento '{documento}' configurado para esta sucursal.")

    siguiente = repository_numerador.siguiente_numerador(db, id_emp, secuencia)
    return siguiente if siguiente is not None else nro_docum_manual


# Paginacion
def get_notas_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(models.NotaFactura).filter(models.NotaFactura.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query \
            .join(models.NotaFactura.cliente) \
            .filter(
                or_(
                    cast(models.NotaFactura.nro_docum, String).ilike(patron),
                    model_cliente.Cliente.nom_cliente.ilike(patron)
                )
            )

    total_records = query.count()

    offset = page * size
    items = query \
        .options(
            joinedload(models.NotaFactura.cliente),
            joinedload(models.NotaFactura.factura_origen)) \
        .order_by(desc(models.NotaFactura.fecha_mod)) \
        .offset(offset) \
        .limit(size) \
        .all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Facturas del cliente, candidatas a ser la "factura origen" de una nota credito.
# A diferencia de compras, t_facturas no tiene Borrador/Finalizado (una venta
# impacta stock/costo de inmediato al guardar), asi que no hace falta filtrar
# por status. texto filtra por numero de documento o serie.
def get_facturas_origen_by_cliente(db: Session, id_emp: int, id_cliente: int, texto: str = None):
    condicion_texto = ""
    params = {"id_emp": id_emp, "id_cliente": id_cliente}
    if texto:
        condicion_texto = "AND (serie_docum||CAST(nro_docum AS TEXT) ILIKE :texto)"
        params["texto"] = f"%{texto}%" 

    return db.execute(
        text(f"""
            SELECT id_trans, nro_docum, serie_docum, fec_doc, imp_total
            FROM t_facturas
            WHERE id_emp = :id_emp AND id_cliente = :id_cliente
            {condicion_texto}
            ORDER BY fec_doc DESC
            LIMIT 20
        """),
        params
    ).mappings().all()


# Lineas de la factura origen, anotadas con el saldo disponible para devolver.
# "cantidad_vendida" ya viene NETA de lo devuelto en notas credito previas de
# esta misma factura origen (para que una factura pueda tener varias notas
# credito sin permitir devolver de nuevo lo que ya se devolvio).
# excluir_id_trans se usa al editar una nota existente, para no restarse a si
# misma de ese acumulado. A diferencia de devolucion a proveedor, NO hay tope
# de stock fisico: la mercancia ENTRA a bodega en vez de salir, el unico tope
# es el saldo de la factura.
def get_lineas_disponibles(db: Session, id_emp: int, id_trans_ref: int, excluir_id_trans: int = None):
    return db.execute(
        text("""
            SELECT
                B.linea,
                B.id_articulo,
                B.id_codbarra,
                B.id_lote,
                COALESCE(M.codigo_lote, '') AS cod_lote,
                COALESCE(C.cod_barra, '') AS cod_articulo,
                COALESCE(C.ref_barra, B.referencia) AS nom_articulo,
                COALESCE(D.maneja_lote, false) AS maneja_lote,
                (B.cantidad - COALESCE(DEV.ya_devuelta, 0)) AS cantidad_vendida,
                B.precio_unit,
                B.impuesto1,
                B.id_tasaimp1,
                COALESCE(I.porc_tasa, 0) AS porc_tasa1
            FROM td_facturas B
            INNER JOIN t_facturas A ON A.id_trans = B.id_trans AND A.id_emp = B.id_emp
            LEFT JOIN m_artxcodigobarra C ON C.id_articulo = B.id_articulo AND C.id_codbarra = B.id_codbarra
            LEFT JOIN m_articulos D ON D.id_articulo = B.id_articulo
            LEFT JOIN m_lotes M ON M.id = B.id_lote
            LEFT JOIN m_impuesto I ON I.id = B.id_tasaimp1
            LEFT JOIN (
                SELECT TD.id_articulo, TD.id_codbarra, TD.id_lote, SUM(TD.cantidad) AS ya_devuelta
                FROM td_notafactura TD
                INNER JOIN t_notafactura T ON T.id_trans = TD.id_trans
                WHERE T.id_trans_ref = :id_trans_ref
                    AND (:excluir_id_trans IS NULL OR TD.id_trans != :excluir_id_trans)
                GROUP BY TD.id_articulo, TD.id_codbarra, TD.id_lote
            ) DEV ON DEV.id_articulo = B.id_articulo AND DEV.id_codbarra = B.id_codbarra AND DEV.id_lote = B.id_lote
            WHERE B.id_trans = :id_trans_ref AND A.id_emp = :id_emp
            ORDER BY B.linea
        """),
        {"id_emp": id_emp, "id_trans_ref": id_trans_ref, "excluir_id_trans": excluir_id_trans}
    ).mappings().all()


def get_nota_by_id(db: Session, id_trans: int):
    nota = db.query(models.NotaFactura).filter(models.NotaFactura.id_trans == id_trans).options(
        joinedload(models.NotaFactura.cliente),
        joinedload(models.NotaFactura.bodega),
        joinedload(models.NotaFactura.factura_origen),
        joinedload(models.NotaFactura.motivo),
        joinedload(models.NotaFactura.detalles)
        .joinedload(models.DetalleNotaFactura.articulo)).first()

    if nota is not None:
        _anotar_cod_lote_y_cantidad_vendida(db, nota)

    return nota


# El detalle guardado (td_notafactura) no conserva el codigo de lote ni la
# cantidad originalmente vendida: se recalculan aqui a partir de m_lotes/td_facturas
# solo para mostrarlos en el formulario de ver/editar (no son columnas propias).
def _anotar_cod_lote_y_cantidad_vendida(db: Session, nota):
    for det in nota.detalles:
        det.cod_lote = ""
        if det.id_lote > 0:
            lote = db.execute(
                text("SELECT codigo_lote FROM m_lotes WHERE id = :id_lote"),
                {"id_lote": det.id_lote}
            ).mappings().first()
            det.cod_lote = lote["codigo_lote"] if lote else ""

        original = db.execute(
            text("""
                SELECT cantidad FROM td_facturas
                WHERE id_trans = :id_trans_ref AND id_articulo = :id_articulo
                    AND id_codbarra = :id_codbarra AND id_lote = :id_lote
            """),
            {
                "id_trans_ref": nota.id_trans_ref,
                "id_articulo": det.id_articulo,
                "id_codbarra": det.id_codbarra,
                "id_lote": det.id_lote
            }
        ).mappings().first()
        det.cantidad_vendida = original["cantidad"] if original else 0


# Crear nota credito. No maneja Borrador/Finalizado: impacta stock (y, segun el
# motivo, caja o saldo a favor) de una vez al guardar.
def create_nota(db: Session, obj: schema_devolucion.NotaFacturaCreate):
    try:
        logs_dict = [log.model_dump() for log in obj.logs]
        nro_docum = _siguiente_nro_docum(db, obj.id_emp, obj.id_sucursal, obj.documento, obj.nro_docum)

        bd_nota = models.NotaFactura(
            id_emp=obj.id_emp,
            id_sucursal=obj.id_sucursal,
            id_cliente=obj.id_cliente,
            id_trans_ref=obj.id_trans_ref,
            id_bodega=obj.id_bodega,
            id_estado=obj.id_estado,
            id_turno=obj.id_turno,
            id_caja=obj.id_caja,
            fec_doc=obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            serie_docum=obj.serie_docum,
            id_motivo=obj.id_motivo,
            observacion=obj.observacion,
            imp_neto=obj.imp_neto,
            impuesto1=obj.impuesto1,
            valor_impuesto1=obj.valor_impuesto1,
            impuesto2=obj.impuesto2,
            valor_impuesto2=obj.valor_impuesto2,
            impuesto3=obj.impuesto3,
            valor_impuesto3=obj.valor_impuesto3,
            imp_total=obj.imp_total,
            vista=obj.vista,
            status=obj.status or 'R',  # 'R' = Registrada; reservado, sin logica todavia
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_nota)
        db.flush()

        _procesar_detalles(db, bd_nota.id_trans, obj)
        db.flush()

        # Impacta p_stock de inmediato (no hay Borrador/Finalizado aqui).
        usuario_mod = logs_dict[-1].get('usuario_mod') if logs_dict else None
        db.execute(
            text("CALL public.sp_ventas_devoluciones(:operacion, :parm_trans, :usuario)"),
            {"operacion": "N", "parm_trans": bd_nota.id_trans, "usuario": usuario_mod}
        )

        db.commit()
        db.refresh(bd_nota)
        return bd_nota

    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))


def update_nota(db: Session, id_trans: int, obj: schema_devolucion.NotaFacturaCreate):
    try:
        bd_nota = db.query(models.NotaFactura).filter(models.NotaFactura.id_trans == id_trans).first()
        if not bd_nota:
            return None

        bd_nota.id_cliente = obj.id_cliente
        bd_nota.id_trans_ref = obj.id_trans_ref
        bd_nota.id_bodega = obj.id_bodega
        bd_nota.id_estado = obj.id_estado
        bd_nota.id_turno = obj.id_turno
        bd_nota.id_caja = obj.id_caja
        bd_nota.fec_doc = obj.fec_doc
        bd_nota.id_motivo = obj.id_motivo
        bd_nota.observacion = obj.observacion
        bd_nota.imp_neto = obj.imp_neto
        bd_nota.impuesto1 = obj.impuesto1
        bd_nota.valor_impuesto1 = obj.valor_impuesto1
        bd_nota.impuesto2 = obj.impuesto2
        bd_nota.valor_impuesto2 = obj.valor_impuesto2
        bd_nota.impuesto3 = obj.impuesto3
        bd_nota.valor_impuesto3 = obj.valor_impuesto3
        bd_nota.imp_total = obj.imp_total
        bd_nota.logs = [log.model_dump() for log in obj.logs]
        bd_nota.fecha_mod = obj.fecha_mod

        db.query(models.DetalleNotaFactura).filter(models.DetalleNotaFactura.id_trans == id_trans).delete()
        db.flush()

        _procesar_detalles(db, id_trans, obj)
        db.flush()

        usuario_mod = bd_nota.logs[-1].get('usuario_mod') if bd_nota.logs else None
        db.execute(
            text("CALL public.sp_ventas_devoluciones(:operacion, :parm_trans, :usuario)"),
            {"operacion": "E", "parm_trans": id_trans, "usuario": usuario_mod}
        )

        db.commit()
        db.refresh(bd_nota)
        return bd_nota

    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))


def delete_nota(db: Session, id_trans: int):
    bd_nota = db.query(models.NotaFactura).filter(models.NotaFactura.id_trans == id_trans).first()
    if not bd_nota:
        return None

    try:
        db.execute(text("DELETE FROM public.p_stock WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})

        db.delete(bd_nota)  # cascade borra el detalle (td_notafactura)
        db.commit()
        return bd_nota
    except Exception:
        db.rollback()
        raise


def _procesar_detalles(db: Session, id_trans: int, obj: schema_devolucion.NotaFacturaCreate):
    for i, det in enumerate(obj.detalles, start=1):
        db.add(models.DetalleNotaFactura(
            id_trans=id_trans,
            linea=i,
            id_articulo=det.id_articulo,
            id_codbarra=det.id_codbarra,
            id_lote=det.id_lote,
            cantidad=det.cantidad,
            precio_unit=det.precio_unit,
            impuesto1=det.impuesto1,
            id_tasaimp1=det.id_tasaimp1,
            valor_impuesto1=det.valor_impuesto1,
            impuesto2=det.impuesto2,
            id_tasaimp2=det.id_tasaimp2,
            valor_impuesto2=det.valor_impuesto2,
            impuesto3=det.impuesto3,
            id_tasaimp3=det.id_tasaimp3,
            valor_impuesto3=det.valor_impuesto3,
            imp_neto=det.imp_neto,
            imp_total=det.imp_total
        ))
