"""fix sp_comercial_ventapos: quitar DELETE preliminar invalido sobre td_abrirturno

Revision ID: 8106e0420f06
Revises: d3f8a291b6c4
Create Date: 2026-08-11 00:00:01.000000

La SP en la BD en vivo tenia un preambulo de 4 DELETE agregado por fuera de
Alembic (no viene de ninguna migracion) - una de esas lineas
('delete from td_abrirturno where id_trans=parm_trans') es invalida porque
esa tabla no tiene columna id_trans (solo id_turno), asi que TODA venta
fallaba de inmediato en esa primera linea. Los otros 3 deletes del
preambulo eran ademas redundantes: el cuerpo ya tiene sus propios
'delete from p_stock'/'delete from p_costos' justo antes de re-insertar
(patron de idempotencia en edicion), y nunca hubo insert/delete propio de
p_movimientocajas fuera de ese lugar. Esta migracion restaura el cuerpo
correcto (el mismo que dejo la migracion d3f8a291b6c4).
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '8106e0420f06'
down_revision = 'd3f8a291b6c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_comercial_ventapos(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
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

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
            from t_facturas A
            inner join td_facturas B On a.id_trans=B.id_trans
            where A.id_trans=parm_trans;

            -- Impacto en costo: una venta NUNCA recalcula el costo promedio ponderado
            -- (eso solo lo hacen las compras, sp_compradirecta) - imp_costo_unitario
            -- queda igual al costo actual, solo baja stock_nuevo (signo=-1). Sin esto,
            -- s_costoxbodegas.cantidad (mantenida solo desde p_costos via el trigger
            -- ins_p_costos/sp_costeo_impacto_costeoxbodega) nunca reflejaba las ventas,
            -- y cada compra posterior recalculaba el promedio contra un stock inflado.
            -- imp_costo_total (cantidad*costo) queda disponible como costo de venta (COGS).
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
                A.vista, null usuario_mod, A.fecha_mod
            from t_facturas A
            inner join td_facturas B on A.id_trans=B.id_trans
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

        END;
        $procedure$
    """)


def downgrade() -> None:
    # No hay una version "anterior valida" a la que volver (la que estaba en
    # vivo antes de esta migracion era la version rota) - downgrade deja la
    # misma definicion (no-op deliberado).
    pass
