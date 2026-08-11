"""monitorcompras_costo_kardex funcion nueva, lee p_costos

Kardex de costos por articulo+bodega, mismo espiritu que monitorstock_kardex
mirando p_stock: en vez de depender de una sola tabla origen (como el viejo
historial que solo leia t_ajustecosto_articulo, perdiendose compras y
devoluciones), lee directo el ledger p_costos - que ya recibe insercion de
sp_compradirecta, sp_compras_devoluciones y sp_ajustecostos por igual. Usa
la columna usuario_mod agregada en la migracion 8f002b62bd05.

Revision ID: b0c94e1907b5
Revises: 192abea6d48d
Create Date: 2026-08-05 18:18:25.099918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0c94e1907b5'
down_revision: Union[str, Sequence[str], None] = '192abea6d48d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION public.monitorcompras_costo_kardex(
            param_id_emp integer, param_id_articulo integer, param_id_bodega integer,
            param_fecha_inicial date, param_fecha_final date)
         RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer,
                       tipo_movimiento character varying, cantidad integer,
                       costo_actual numeric, costo_nuevo numeric, costo_unitario numeric,
                       stock_actual integer, stock_nuevo integer, vista character varying,
                       usuario_mod character varying)
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                P.fec_doc,
                P.documento,
                P.nro_docum,
                CASE WHEN P.signo >= 0 THEN 'Entrada' ELSE 'Salida' END::character varying as tipo_movimiento,
                P.cantidad,
                P.imp_costo_actual,
                P.imp_costo_nuevo,
                P.imp_costo_unitario,
                P.stock_actual,
                P.stock_nuevo,
                P.vista,
                P.usuario_mod
            FROM p_costos P
            WHERE P.id_emp = param_id_emp
              AND P.id_articulo = param_id_articulo
              AND P.id_bodega = param_id_bodega
              AND (param_fecha_inicial IS NULL OR P.fec_doc >= param_fecha_inicial)
              AND (param_fecha_final IS NULL OR P.fec_doc <= param_fecha_final)
            ORDER BY P.fec_doc, P.id_trans;
        END;
        $function$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS public.monitorcompras_costo_kardex(integer, integer, integer, date, date)")
