"""s_costovariacion agregar stock_anterior

Contexto visible en la fila del kardex: el usuario ve "Costo Anterior" y
preguntó por que no hay tambien un "Stock Anterior" (cuanto habia antes de
esta entrada) - viene gratis de p_costos.stock_actual, solo faltaba copiarlo.

Revision ID: 32eb6e603dcd
Revises: da6b7b5e8db0
Create Date: 2026-08-05 19:38:30.477185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32eb6e603dcd'
down_revision: Union[str, Sequence[str], None] = 'da6b7b5e8db0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.s_costovariacion ADD COLUMN IF NOT EXISTS stock_anterior integer")

    op.execute("""
        UPDATE public.s_costovariacion V
        SET stock_anterior = P.stock_actual
        FROM public.p_costos P
        WHERE P.id_trans = V.id_trans AND P.linea = V.linea
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_costos_variacion_insert()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF NEW.imp_costo_unitario IS DISTINCT FROM NEW.imp_costo_actual THEN
                INSERT INTO public.s_costovariacion (
                    id_trans, linea, id_emp, id_bodega, id_articulo, id_proveedor, fec_doc,
                    documento, nro_docum, vista, cantidad, stock_anterior, costo_anterior,
                    costo_movimiento, costo_nuevo_promedio, usuario_mod, fecha_mod)
                VALUES (
                    NEW.id_trans, NEW.linea, NEW.id_emp, NEW.id_bodega, NEW.id_articulo,
                    NULLIF(NEW.id_proveedor, 0), NEW.fec_doc, NEW.documento, NEW.nro_docum,
                    NEW.vista, NEW.cantidad, NEW.stock_actual, NEW.imp_costo_actual,
                    NEW.imp_costo_nuevo, NEW.imp_costo_unitario, NEW.usuario_mod, NEW.fecha_mod)
                ON CONFLICT (id_trans, linea) DO UPDATE SET
                    id_emp = EXCLUDED.id_emp, id_bodega = EXCLUDED.id_bodega,
                    id_articulo = EXCLUDED.id_articulo, id_proveedor = EXCLUDED.id_proveedor,
                    fec_doc = EXCLUDED.fec_doc, documento = EXCLUDED.documento,
                    nro_docum = EXCLUDED.nro_docum, vista = EXCLUDED.vista,
                    cantidad = EXCLUDED.cantidad, stock_anterior = EXCLUDED.stock_anterior,
                    costo_anterior = EXCLUDED.costo_anterior,
                    costo_movimiento = EXCLUDED.costo_movimiento,
                    costo_nuevo_promedio = EXCLUDED.costo_nuevo_promedio,
                    usuario_mod = EXCLUDED.usuario_mod, fecha_mod = EXCLUDED.fecha_mod;
            END IF;
            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("DROP FUNCTION IF EXISTS public.monitorcompras_costo_kardex(integer, integer, integer)")
    op.execute("""
        CREATE FUNCTION public.monitorcompras_costo_kardex(
            param_id_emp integer, param_id_articulo integer, param_id_bodega integer)
         RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer,
                       vista character varying, cantidad integer, stock_anterior integer,
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
                V.stock_anterior,
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

    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_costos_variacion_insert()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF NEW.imp_costo_unitario IS DISTINCT FROM NEW.imp_costo_actual THEN
                INSERT INTO public.s_costovariacion (
                    id_trans, linea, id_emp, id_bodega, id_articulo, id_proveedor, fec_doc,
                    documento, nro_docum, vista, cantidad, costo_anterior, costo_movimiento,
                    costo_nuevo_promedio, usuario_mod, fecha_mod)
                VALUES (
                    NEW.id_trans, NEW.linea, NEW.id_emp, NEW.id_bodega, NEW.id_articulo,
                    NULLIF(NEW.id_proveedor, 0), NEW.fec_doc, NEW.documento, NEW.nro_docum,
                    NEW.vista, NEW.cantidad, NEW.imp_costo_actual, NEW.imp_costo_nuevo,
                    NEW.imp_costo_unitario, NEW.usuario_mod, NEW.fecha_mod)
                ON CONFLICT (id_trans, linea) DO UPDATE SET
                    id_emp = EXCLUDED.id_emp, id_bodega = EXCLUDED.id_bodega,
                    id_articulo = EXCLUDED.id_articulo, id_proveedor = EXCLUDED.id_proveedor,
                    fec_doc = EXCLUDED.fec_doc, documento = EXCLUDED.documento,
                    nro_docum = EXCLUDED.nro_docum, vista = EXCLUDED.vista,
                    cantidad = EXCLUDED.cantidad, costo_anterior = EXCLUDED.costo_anterior,
                    costo_movimiento = EXCLUDED.costo_movimiento,
                    costo_nuevo_promedio = EXCLUDED.costo_nuevo_promedio,
                    usuario_mod = EXCLUDED.usuario_mod, fecha_mod = EXCLUDED.fecha_mod;
            END IF;
            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("ALTER TABLE public.s_costovariacion DROP COLUMN IF EXISTS stock_anterior")
