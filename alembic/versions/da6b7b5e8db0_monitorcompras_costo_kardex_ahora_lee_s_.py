"""monitorcompras_costo_kardex ahora lee s_costovariacion, sin filtro de fechas

s_costovariacion ya viene pre-filtrada a solo cambios reales (ver
ad0ac75b0914), asi que el filtro de fecha en el kardex dejo de tener sentido:
la tabla origen es chica por construccion (una fila por cambio real de costo
en toda la vida del articulo+bodega, no una fila por venta/compra), no hay
volumen que cuidar. Se trae todo el historial sin LIMIT, mas rapido y simple
que reconstruir "solo cambios" a partir de p_costos en cada consulta.

Revision ID: da6b7b5e8db0
Revises: ad0ac75b0914
Create Date: 2026-08-05 19:21:54.998255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da6b7b5e8db0'
down_revision: Union[str, Sequence[str], None] = 'ad0ac75b0914'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS public.monitorcompras_costo_kardex(integer, integer, integer, date, date)")
    op.execute("""
        CREATE FUNCTION public.monitorcompras_costo_kardex(
            param_id_emp integer, param_id_articulo integer, param_id_bodega integer)
         RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer,
                       vista character varying, cantidad integer,
                       costo_anterior numeric, costo_movimiento numeric, costo_nuevo_promedio numeric,
                       usuario_mod character varying)
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                V.fec_doc,
                V.documento,
                V.nro_docum,
                V.vista,
                V.cantidad,
                V.costo_anterior,
                V.costo_movimiento,
                V.costo_nuevo_promedio,
                V.usuario_mod
            FROM s_costovariacion V
            WHERE V.id_emp = param_id_emp
              AND V.id_articulo = param_id_articulo
              AND V.id_bodega = param_id_bodega
            ORDER BY V.fec_doc, V.id_trans;
        END;
        $function$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS public.monitorcompras_costo_kardex(integer, integer, integer)")
    op.execute("""
        CREATE FUNCTION public.monitorcompras_costo_kardex(
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
