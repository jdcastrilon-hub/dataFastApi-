"""p_costos agregar usuario_mod y SPs compras/ajustecostos/devoluciones

p_costos es un ledger al que escriben 3 SPs distintos (sp_compradirecta,
sp_compras_devoluciones, sp_ajustecostos), asi que hoy no hay forma de saber
"quien" genero un cambio de costo sin ir a buscar el logs JSON del documento
origen especifico (compra/devolucion/ajuste) caso por caso. Mismo problema que
ya se habia resuelto para p_precios (ver esa tabla: columna usuario_mod
poblada directo al insertar, sin depender de logs). Se replica aqui.

Los 3 SPs no reciben el usuario desde ningun contexto de sesion (Python los
llama solo con operacion/parm_trans) - se les agrega un tercer parametro
p_usuario (con DEFAULT NULL, para no romper llamadas viejas), que Python
ahora puebla extrayendolo del ultimo log del documento (obj.logs[-1].usuario_mod),
igual que ya hacia get_historial_ajustes() para mostrar "quien" en el historial
manual. p_stock queda fuera de alcance por ahora (decision explicita del
usuario: solo p_costos por esta vez).

Revision ID: 8f002b62bd05
Revises: 5eed58b4477d
Create Date: 2026-08-02 18:43:47.400239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f002b62bd05'
down_revision: Union[str, Sequence[str], None] = '5eed58b4477d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.p_costos ADD COLUMN IF NOT EXISTS usuario_mod character varying(50)")

    op.execute("DROP PROCEDURE IF EXISTS public.sp_ajustecostos(character varying, integer)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ajustecostos(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL)
         LANGUAGE plpgsql
        AS $procedure$

        BEGIN
            --Borramos Costos
            delete from p_costos where id_trans=parm_trans;

            --Insertamos costos
            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            select A.id_trans,1 linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,0 id_proveedor,A.fec_doc,
            a.id_articulo,0 cantidad,1 signo,imp_costo_actual,imp_costo_nuevo,0 imp_costo_adicional,
            B.cantidad stock_actual,
            B.cantidad stock_nuevo,
            cast((imp_costo_nuevo*B.cantidad) as numeric(20,2)) imp_costo_total,
            imp_costo_nuevo imp_costo_unitario,
            A.vista, p_usuario, A.fecha_mod
            from t_ajustecosto_articulo A
            left join (select id_bodega,id_articulo,sum(cantidad) cantidad from s_stkbodegas
                        group by id_bodega,id_articulo) B on A.id_bodega=B.id_bodega and A.id_articulo=B.id_articulo
            where A.id_trans=parm_trans;


        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE IF EXISTS public.sp_compradirecta(character varying, integer)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL)
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
            --(stock actual * costo actual)+ Costo total compra) / (stock actual + cantidad comprada)
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

    op.execute("DROP PROCEDURE IF EXISTS public.sp_compras_devoluciones(character varying, integer)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compras_devoluciones(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL)
         LANGUAGE plpgsql
        AS $procedure$

        BEGIN
            -- Idempotente: borra cualquier impacto previo de esta transaccion antes de re-insertar
            -- (permite reintentos y ediciones sin duplicar movimientos).
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            -- Insertamos costos PRIMERO (antes de tocar p_stock): s_stkbodegas/s_costoxbodegas
            -- se recalculan a partir de p_stock (via trigger), asi que si insertaramos el
            -- stock antes, aqui ya leeriamos el saldo DESPUES del movimiento en vez de antes
            -- (mismo orden que ya usa sp_compradirecta, por la misma razon).
            -- Valorado al costo promedio ACTUAL de la bodega/articulo (sacar unidades no
            -- cambia el promedio de lo que queda, no se usa el costo historico de la compra
            -- origen). id_trans_ref/documento_ref/nro_docum_ref quedan apuntando a la compra origen.
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

            -- Insertamos Stock DESPUES: una devolucion siempre es una salida (signo -1).
            -- documento_ref/nro_ref quedan apuntando a la compra origen, para trazabilidad.
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


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP PROCEDURE IF EXISTS public.sp_ajustecostos(character varying, integer, character varying)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ajustecostos(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$

        BEGIN
            --Borramos Costos
            delete from p_costos where id_trans=parm_trans;

            --Insertamos costos
            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, fecha_mod)
            select A.id_trans,1 linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,0 id_proveedor,A.fec_doc,
            a.id_articulo,0 cantidad,1 signo,imp_costo_actual,imp_costo_nuevo,0 imp_costo_adicional,
            B.cantidad stock_actual,
            B.cantidad stock_nuevo,
            cast((imp_costo_nuevo*B.cantidad) as numeric(20,2)) imp_costo_total,
            imp_costo_nuevo imp_costo_unitario,
            A.vista,A.fecha_mod
            from t_ajustecosto_articulo A
            left join (select id_bodega,id_articulo,sum(cantidad) cantidad from s_stkbodegas
                        group by id_bodega,id_articulo) B on A.id_bodega=B.id_bodega and A.id_articulo=B.id_articulo
            where A.id_trans=parm_trans;


        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE IF EXISTS public.sp_compradirecta(character varying, integer, character varying)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer)
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
            imp_costo_total, imp_costo_unitario, vista, fecha_mod)
            select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
            b.id_articulo,b.cantidad,1 signo,
            COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
            B.costo_unit imp_costo_nuevo,
            0 imp_costo_adicional,
            COALESCE(D.cantidad, 0) stock_actual,
            (B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
            cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
            cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
            A.vista,A.fecha_mod
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

    op.execute("DROP PROCEDURE IF EXISTS public.sp_compras_devoluciones(character varying, integer, character varying)")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_compras_devoluciones(IN operacion character varying, IN parm_trans integer)
         LANGUAGE plpgsql
        AS $procedure$

        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;
            DELETE FROM p_costos WHERE id_trans = parm_trans;

            INSERT INTO p_costos(
            id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
            id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
            stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod)
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
                   A.vista, A.fecha_mod
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

    op.execute("ALTER TABLE public.p_costos DROP COLUMN IF EXISTS usuario_mod")
