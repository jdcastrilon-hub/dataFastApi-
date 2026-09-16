"""p_stock agregar usuario_mod y propagar p_usuario en los 7 sp que lo escriben

Mismo tratamiento que p_costos/p_precios (ver migracion 8f002b62bd05): agrega
usuario_mod a p_stock, poblado directo al insertar, no derivado. A diferencia
de p_costos (solo 3 escritores), p_stock lo escriben 7 SPs - todo el sistema
que mueve inventario:

- sp_compradirecta, sp_compras_devoluciones, sp_ventas_devoluciones ya
  reciben "p_usuario" (de la migracion de p_costos) pero nunca lo usaban en su
  propio INSERT INTO p_stock - solo hace falta agregarlo ahi, sin cambiar la
  firma (CREATE OR REPLACE simple).
- sp_stock_impacto_ajustestock, sp_stock_impacto_trasladobodega,
  sp_stock_impacto_cargastock, sp_comercial_ventapos NUNCA tuvieron el
  parametro - hay que agregarlo, lo que cambia la firma y obliga a
  DROP PROCEDURE + CREATE (gotcha ya conocido: CREATE OR REPLACE con una
  firma distinta crea un overload nuevo en vez de reemplazar).

Bonus fix de paso en sp_comercial_ventapos: su propio INSERT INTO p_costos ya
tiene la columna usuario_mod pero la poblaba con "null" hardcodeado (nunca se
le agrego el parametro cuando se hizo la migracion de p_costos) - ahora que
el parametro existe, se usa ahi tambien.

Revision ID: 50b2e2eb5aac
Revises: 80ba34ab144a
Create Date: 2026-08-24 18:25:49.379239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50b2e2eb5aac'
down_revision: Union[str, Sequence[str], None] = '80ba34ab144a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.p_stock ADD COLUMN usuario_mod character varying;")

    # --- Grupo A: ya reciben p_usuario, solo falta usarlo en su INSERT a p_stock ---

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            INSERT INTO public.m_artxcodigobarra(
            id_articulo, id_codbarra, cod_barra, ref_barra)
            select id_articulo, id_codbarra, cod_barra, ref_barra
            FROM public.td_comprasnewcodbarra where id_trans=parm_trans;

            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_comprasnuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
            b.id_articulo,b.cantidad,1 signo,
            COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
            B.costo_unit imp_costo_nuevo,
            0 imp_costo_adicional,
            COALESCE(D.cantidad, 0) stock_actual,
            (B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
            cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
            cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
            A.vista, p_usuario, A.fecha_mod
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compras_devoluciones(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            INSERT INTO p_costos(
            id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
            id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
            stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, A.id_compra_origen, A.documento, A.nro_docum,
                   C.documento, C.nro_docum, A.id_proveedor, A.fec_doc,
                   B.id_articulo, B.cantidad, -1 signo,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_actual,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_nuevo,
                   0 imp_costo_adicional,
                   COALESCE(E.cantidad, 0) stock_actual,
                   (COALESCE(E.cantidad, 0) - B.cantidad) stock_nuevo,
                   cast((COALESCE(D.imp_costo_unitario, 0) * B.cantidad) as numeric(20,2)) imp_costo_total,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_unitario,
                   A.vista, p_usuario, A.fecha_mod
            FROM t_devolucioncompras A
            INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
            INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            LEFT JOIN s_stkbodegas E ON A.id_bodega = E.id_bodega AND B.id_articulo = E.id_articulo
                   AND A.id_estado = E.id_estado AND B.id_codbarra = E.id_codbarra
            WHERE A.id_trans = parm_trans;

            INSERT INTO p_stock
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
                   B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
                   B.cantidad, -1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod, p_usuario
            FROM t_devolucioncompras A
            INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
            INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
            WHERE A.id_trans = parm_trans;

        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ventas_devoluciones(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;

            INSERT INTO p_stock
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
                   B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
                   B.cantidad, 1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod, p_usuario
            FROM t_notafactura A
            INNER JOIN td_notafactura B ON A.id_trans = B.id_trans
            INNER JOIN t_facturas C ON A.id_trans_ref = C.id_trans AND A.id_emp = C.id_emp
            WHERE A.id_trans = parm_trans;
        END;
        $procedure$;
    """)

    # --- Grupo B: nunca tuvieron p_usuario - cambia la firma, hay que DROP + CREATE ---

    op.execute("DROP PROCEDURE public.sp_stock_impacto_ajustestock(character varying, integer);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_ajustestock(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_ajustestocknuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, C.signo,
                COALESCE(D.imp_costo_unitario, 0),
                COALESCE(D.imp_costo_unitario, 0),
                0,
                COALESCE(D.cantidad, 0),
                (COALESCE(D.cantidad, 0) + (B.cantidad * C.signo)),
                CAST((B.cantidad * COALESCE(D.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(COALESCE(D.imp_costo_unitario, 0) AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_ajustestock A
            INNER JOIN td_ajustestock B ON A.id_trans = B.id_trans
            INNER JOIN m_motivoajuste C ON A.id_motivo = C.id
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,B.id_ubicacion,
            B.cantidad,c.signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_ajustestock A
            inner join td_ajustestock B On a.id_trans=B.id_trans
            inner join m_motivoajuste C on A.id_motivo=C.id
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_stock_impacto_trasladobodega(character varying, integer);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_trasladobodega(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega_origen, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, -1,
                COALESCE(D.imp_costo_unitario, 0),
                COALESCE(D.imp_costo_unitario, 0),
                0,
                COALESCE(D.cantidad, 0),
                (COALESCE(D.cantidad, 0) - B.cantidad),
                CAST((B.cantidad * COALESCE(D.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(COALESCE(D.imp_costo_unitario, 0) AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_trasladobodega A
            INNER JOIN td_trasladobodega B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega_origen = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans
              AND A.id_bodega_origen <> A.id_bodega_destino;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans,
                B.linea + (SELECT COUNT(*) FROM td_trasladobodega WHERE id_trans = A.id_trans),
                A.id_emp, A.id_bodega_destino, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, 1,
                COALESCE(ORIG.imp_costo_unitario, 0),
                COALESCE(ORIG.imp_costo_unitario, 0),
                0,
                COALESCE(DEST.cantidad, 0),
                (COALESCE(DEST.cantidad, 0) + B.cantidad),
                CAST((B.cantidad * COALESCE(ORIG.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(
                    ((COALESCE(DEST.cantidad,0) * COALESCE(DEST.imp_costo_unitario,0)) + (B.cantidad * COALESCE(ORIG.imp_costo_unitario,0)))
                    / NULLIF((B.cantidad + COALESCE(DEST.cantidad,0)), 0)
                AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_trasladobodega A
            INNER JOIN td_trasladobodega B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas ORIG ON A.id_bodega_origen = ORIG.id_bodega AND B.id_articulo = ORIG.id_articulo
            LEFT JOIN s_costoxbodegas DEST ON A.id_bodega_destino = DEST.id_bodega AND B.id_articulo = DEST.id_articulo
            WHERE A.id_trans = parm_trans
              AND A.id_bodega_origen <> A.id_bodega_destino;

            insert into p_stock (id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod, usuario_mod)
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega_origen,a.id_estado_origen,B.id_lote,B.id_ubicacion,
            B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_trasladobodega A
            inner join td_trasladobodega B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

            insert into p_stock (id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod, usuario_mod)
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega_destino,a.id_estado_destino,B.id_lote,B.id_ubicacion,
            B.cantidad,1 signo,null,A.vista,
            B.linea + (SELECT COUNT(*) FROM td_trasladobodega WHERE id_trans = A.id_trans),
            'Imp2',A.fecha_mod,p_usuario
            from t_trasladobodega A
            inner join td_trasladobodega B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_stock_impacto_cargastock(character varying, integer);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_cargastock(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, 0, A.documento, A.nro_docum, NULL, NULL,
                A.id_proveedor, A.fecha_movimiento, B.id_articulo, B.cantidad, 1,
                COALESCE(D.imp_costo_unitario, 0),
                B.costo,
                0,
                COALESCE(D.cantidad, 0),
                (B.cantidad + COALESCE(D.cantidad, 0)),
                CAST((B.costo * B.cantidad) AS numeric(20,2)),
                CAST(B.costo AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_cargastock A
            INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans;

            INSERT INTO p_stock (
                id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod, usuario_mod
            )
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, NULL, NULL, A.fecha_movimiento,
                B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, B.id_ubicacion,
                B.cantidad, 1, NULL, A.vista, B.linea, 'Imp', A.fecha_mod, p_usuario
            FROM t_cargastock A
            INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
            WHERE A.id_trans = parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_comercial_ventapos(character varying, integer);")
    op.execute("""
        CREATE PROCEDURE public.sp_comercial_ventapos(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN

            delete from td_abrirturno where id_referencia=parm_trans;
            delete from p_movimientocajas where id_trans=parm_trans;
            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO public.td_abrirturno(
                id_turno, concepto, fecha, id_referencia, id_mediopago, importe, signo, vista)
            SELECT f.id_turno, 'Factura', f.fecha_mod, f.id_trans, m.id_mediopago, m.importe, 1, f.vista
            FROM t_facturas f
            JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
            WHERE f.id_trans = parm_trans AND f.id_turno IS NOT NULL;

            INSERT INTO public.p_movimientocajas(
                id_trans, linea, id_emp, id_caja, id_mediopago, concepto, id_referencia, fec_doc, importe, signo, vista)
            SELECT f.id_trans, m.linea, f.id_emp, f.id_caja, m.id_mediopago, 'Factura', f.id_trans, f.fec_doc, m.importe, 1, f.vista
            FROM t_facturas f
            JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
            WHERE f.id_trans = parm_trans AND f.id_turno IS NULL AND f.id_caja IS NOT NULL;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_facturas A
            inner join td_facturas B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

            insert into p_costos(
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo,
                imp_costo_adicional, stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario,
                vista, usuario_mod, fecha_mod)
            select A.id_trans, B.linea, A.id_emp, A.id_bodega, 0 id_trans_ref, A.documento, A.nro_docum, null, null,
                0 id_proveedor, A.fec_doc, B.id_articulo, B.cantidad, -1 signo,
                COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
                COALESCE(D.imp_costo_unitario,0) imp_costo_nuevo,
                0 imp_costo_adicional,
                COALESCE(D.cantidad,0) stock_actual,
                (COALESCE(D.cantidad,0) - B.cantidad) stock_nuevo,
                cast((COALESCE(D.imp_costo_unitario,0) * B.cantidad) as numeric(20,2)) imp_costo_total,
                COALESCE(D.imp_costo_unitario,0) imp_costo_unitario,
                A.vista, p_usuario, A.fecha_mod
            from t_facturas A
            inner join td_facturas B on A.id_trans=B.id_trans
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP PROCEDURE public.sp_comercial_ventapos(character varying, integer, character varying);")
    op.execute("""
        CREATE PROCEDURE public.sp_comercial_ventapos(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN

            delete from td_abrirturno where id_referencia=parm_trans;
            delete from p_movimientocajas where id_trans=parm_trans;
            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO public.td_abrirturno(
                id_turno, concepto, fecha, id_referencia, id_mediopago, importe, signo, vista)
            SELECT f.id_turno, 'Factura', f.fecha_mod, f.id_trans, m.id_mediopago, m.importe, 1, f.vista
            FROM t_facturas f
            JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
            WHERE f.id_trans = parm_trans AND f.id_turno IS NOT NULL;

            INSERT INTO public.p_movimientocajas(
                id_trans, linea, id_emp, id_caja, id_mediopago, concepto, id_referencia, fec_doc, importe, signo, vista)
            SELECT f.id_trans, m.linea, f.id_emp, f.id_caja, m.id_mediopago, 'Factura', f.id_trans, f.fec_doc, m.importe, 1, f.vista
            FROM t_facturas f
            JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
            WHERE f.id_trans = parm_trans AND f.id_turno IS NULL AND f.id_caja IS NOT NULL;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
            from t_facturas A
            inner join td_facturas B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

            insert into p_costos(
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo,
                imp_costo_adicional, stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario,
                vista, usuario_mod, fecha_mod)
            select A.id_trans, B.linea, A.id_emp, A.id_bodega, 0 id_trans_ref, A.documento, A.nro_docum, null, null,
                0 id_proveedor, A.fec_doc, B.id_articulo, B.cantidad, -1 signo,
                COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
                COALESCE(D.imp_costo_unitario,0) imp_costo_nuevo,
                0 imp_costo_adicional,
                COALESCE(D.cantidad,0) stock_actual,
                (COALESCE(D.cantidad,0) - B.cantidad) stock_nuevo,
                cast((COALESCE(D.imp_costo_unitario,0) * B.cantidad) as numeric(20,2)) imp_costo_total,
                COALESCE(D.imp_costo_unitario,0) imp_costo_unitario,
                A.vista, null, A.fecha_mod
            from t_facturas A
            inner join td_facturas B on A.id_trans=B.id_trans
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_stock_impacto_cargastock(character varying, integer, character varying);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_cargastock(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, 0, A.documento, A.nro_docum, NULL, NULL,
                A.id_proveedor, A.fecha_movimiento, B.id_articulo, B.cantidad, 1,
                COALESCE(D.imp_costo_unitario, 0),
                B.costo,
                0,
                COALESCE(D.cantidad, 0),
                (B.cantidad + COALESCE(D.cantidad, 0)),
                CAST((B.costo * B.cantidad) AS numeric(20,2)),
                CAST(B.costo AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_cargastock A
            INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans;

            INSERT INTO p_stock (
                id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod
            )
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, NULL, NULL, A.fecha_movimiento,
                B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, B.id_ubicacion,
                B.cantidad, 1, NULL, A.vista, B.linea, 'Imp', A.fecha_mod
            FROM t_cargastock A
            INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
            WHERE A.id_trans = parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_stock_impacto_trasladobodega(character varying, integer, character varying);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_trasladobodega(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega_origen, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, -1,
                COALESCE(D.imp_costo_unitario, 0),
                COALESCE(D.imp_costo_unitario, 0),
                0,
                COALESCE(D.cantidad, 0),
                (COALESCE(D.cantidad, 0) - B.cantidad),
                CAST((B.cantidad * COALESCE(D.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(COALESCE(D.imp_costo_unitario, 0) AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_trasladobodega A
            INNER JOIN td_trasladobodega B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega_origen = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans
              AND A.id_bodega_origen <> A.id_bodega_destino;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans,
                B.linea + (SELECT COUNT(*) FROM td_trasladobodega WHERE id_trans = A.id_trans),
                A.id_emp, A.id_bodega_destino, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, 1,
                COALESCE(ORIG.imp_costo_unitario, 0),
                COALESCE(ORIG.imp_costo_unitario, 0),
                0,
                COALESCE(DEST.cantidad, 0),
                (COALESCE(DEST.cantidad, 0) + B.cantidad),
                CAST((B.cantidad * COALESCE(ORIG.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(
                    ((COALESCE(DEST.cantidad,0) * COALESCE(DEST.imp_costo_unitario,0)) + (B.cantidad * COALESCE(ORIG.imp_costo_unitario,0)))
                    / NULLIF((B.cantidad + COALESCE(DEST.cantidad,0)), 0)
                AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_trasladobodega A
            INNER JOIN td_trasladobodega B ON A.id_trans = B.id_trans
            LEFT JOIN s_costoxbodegas ORIG ON A.id_bodega_origen = ORIG.id_bodega AND B.id_articulo = ORIG.id_articulo
            LEFT JOIN s_costoxbodegas DEST ON A.id_bodega_destino = DEST.id_bodega AND B.id_articulo = DEST.id_articulo
            WHERE A.id_trans = parm_trans
              AND A.id_bodega_origen <> A.id_bodega_destino;

            insert into p_stock (id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod)
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega_origen,a.id_estado_origen,B.id_lote,B.id_ubicacion,
            B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
            from t_trasladobodega A
            inner join td_trasladobodega B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

            insert into p_stock (id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
                id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
                cantidad, signo, fec_venc, vista, linea, serie, fecha_mod)
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega_destino,a.id_estado_destino,B.id_lote,B.id_ubicacion,
            B.cantidad,1 signo,null,A.vista,
            B.linea + (SELECT COUNT(*) FROM td_trasladobodega WHERE id_trans = A.id_trans),
            'Imp2',A.fecha_mod
            from t_trasladobodega A
            inner join td_trasladobodega B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE public.sp_stock_impacto_ajustestock(character varying, integer, character varying);")
    op.execute("""
        CREATE PROCEDURE public.sp_stock_impacto_ajustestock(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_ajustestocknuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO p_costos (
                id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
                id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
                stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
            )
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, 0, A.documento, A.nro_docum, NULL, NULL,
                0, A.fecha_movimiento, B.id_articulo, B.cantidad, C.signo,
                COALESCE(D.imp_costo_unitario, 0),
                COALESCE(D.imp_costo_unitario, 0),
                0,
                COALESCE(D.cantidad, 0),
                (COALESCE(D.cantidad, 0) + (B.cantidad * C.signo)),
                CAST((B.cantidad * COALESCE(D.imp_costo_unitario, 0)) AS numeric(20,2)),
                CAST(COALESCE(D.imp_costo_unitario, 0) AS numeric(20,2)),
                A.vista, A.fecha_mod
            FROM t_ajustestock A
            INNER JOIN td_ajustestock B ON A.id_trans = B.id_trans
            INNER JOIN m_motivoajuste C ON A.id_motivo = C.id
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            WHERE A.id_trans = parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,B.id_ubicacion,
            B.cantidad,c.signo,null,A.vista,B.linea,'Imp',A.fecha_mod
            from t_ajustestock A
            inner join td_ajustestock B On a.id_trans=B.id_trans
            inner join m_motivoajuste C on A.id_motivo=C.id
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ventas_devoluciones(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;

            INSERT INTO p_stock
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
                   B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
                   B.cantidad, 1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod
            FROM t_notafactura A
            INNER JOIN td_notafactura B ON A.id_trans = B.id_trans
            INNER JOIN t_facturas C ON A.id_trans_ref = C.id_trans AND A.id_emp = C.id_emp
            WHERE A.id_trans = parm_trans;
        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compras_devoluciones(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            INSERT INTO p_costos(
            id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
            id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
            stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, A.id_compra_origen, A.documento, A.nro_docum,
                   C.documento, C.nro_docum, A.id_proveedor, A.fec_doc,
                   B.id_articulo, B.cantidad, -1 signo,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_actual,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_nuevo,
                   0 imp_costo_adicional,
                   COALESCE(E.cantidad, 0) stock_actual,
                   (COALESCE(E.cantidad, 0) - B.cantidad) stock_nuevo,
                   cast((COALESCE(D.imp_costo_unitario, 0) * B.cantidad) as numeric(20,2)) imp_costo_total,
                   COALESCE(D.imp_costo_unitario, 0) imp_costo_unitario,
                   A.vista, p_usuario, A.fecha_mod
            FROM t_devolucioncompras A
            INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
            INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
            LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
            LEFT JOIN s_stkbodegas E ON A.id_bodega = E.id_bodega AND B.id_articulo = E.id_articulo
                   AND A.id_estado = E.id_estado AND B.id_codbarra = E.id_codbarra
            WHERE A.id_trans = parm_trans;

            INSERT INTO p_stock
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
                   B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
                   B.cantidad, -1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod
            FROM t_devolucioncompras A
            INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
            INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
            WHERE A.id_trans = parm_trans;

        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            INSERT INTO public.m_artxcodigobarra(
            id_articulo, id_codbarra, cod_barra, ref_barra)
            select id_articulo, id_codbarra, cod_barra, ref_barra
            FROM public.td_comprasnewcodbarra where id_trans=parm_trans;

            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_comprasnuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
            b.id_articulo,b.cantidad,1 signo,
            COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
            B.costo_unit imp_costo_nuevo,
            0 imp_costo_adicional,
            COALESCE(D.cantidad, 0) stock_actual,
            (B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
            cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
            cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
            A.vista, p_usuario, A.fecha_mod
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            where A.id_trans=parm_trans;

        END;
        $procedure$;
    """)

    op.execute("ALTER TABLE public.p_stock DROP COLUMN usuario_mod;")
