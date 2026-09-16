"""sp_ajustecostos coalesce stock_actual sin movimiento previo

Revision ID: c8255c74d8be
Revises: 83c4a4f15537
Create Date: 2026-09-08 19:22:09.212946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8255c74d8be'
down_revision: Union[str, Sequence[str], None] = '83c4a4f15537'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    sp_ajustecostos leia stock_actual via LEFT JOIN contra s_stkbodegas sin
    COALESCE - para un articulo/bodega que nunca tuvo NINGUNA fila en
    s_stkbodegas (recien creado, jamas movido), B.cantidad llega NULL y viola
    el NOT NULL de p_costos.stock_actual/stock_nuevo/imp_costo_total. Mismo
    patron COALESCE(...,0) que ya usan sp_compradirecta/sp_stock_impacto_*
    para imp_costo_actual/imp_costo_nuevo cuando no hay costo previo.
    """
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ajustecostos(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
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
                    COALESCE(B.cantidad, 0) stock_actual,
                    COALESCE(B.cantidad, 0) stock_nuevo,
                    cast((imp_costo_nuevo*COALESCE(B.cantidad, 0)) as numeric(20,2)) imp_costo_total,
                    imp_costo_nuevo imp_costo_unitario,
                    A.vista, p_usuario, A.fecha_mod
                    from t_ajustecosto_articulo A
                    left join (select id_bodega,id_articulo,sum(cantidad) cantidad from s_stkbodegas
                                group by id_bodega,id_articulo) B on A.id_bodega=B.id_bodega and A.id_articulo=B.id_articulo
                    where A.id_trans=parm_trans;


                END;
                $procedure$
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ajustecostos(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
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
                $procedure$
    """)
