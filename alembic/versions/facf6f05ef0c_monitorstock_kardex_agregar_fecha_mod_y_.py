"""monitorstock_kardex agregar fecha_mod y usuario_mod

Expone en el kardex de inventario las dos columnas que la migracion
50b2e2eb5aac acaba de agregar a p_stock. Cambia el RETURNS TABLE de la
funcion, asi que no alcanza con CREATE OR REPLACE (Postgres no permite
cambiar el tipo de retorno de una funcion existente) - hace falta
DROP FUNCTION + CREATE.

Revision ID: facf6f05ef0c
Revises: 50b2e2eb5aac
Create Date: 2026-08-24 18:36:27.057470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'facf6f05ef0c'
down_revision: Union[str, Sequence[str], None] = '50b2e2eb5aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP FUNCTION public.monitorstock_kardex(integer, integer, date, date);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_kardex(param_id_articulo integer, param_id_codbarra integer, param_fecha_inicial date, param_fecha_final date)
         RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer, bodega character varying, estado character varying, tipo_movimiento character varying, cantidad integer, vista character varying, fecha_mod timestamp without time zone, usuario_mod character varying)
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                P.fec_doc,
                P.documento,
                P.nro_docum,
                COALESCE(B.nom_bodega, 'Sin Bodega')::character varying as bodega,
                COALESCE(E.cod_estado, '')::character varying as estado,
                CASE WHEN P.signo >= 0 THEN 'Entrada' ELSE 'Salida' END::character varying as tipo_movimiento,
                P.cantidad,
                P.vista,
                P.fecha_mod,
                P.usuario_mod
            FROM p_stock P
            LEFT JOIN m_bodegas B ON P.id_bodega = B.id
            LEFT JOIN m_estados E ON P.id_estado = E.id
            WHERE P.id_articulo = param_id_articulo
              AND P.id_codbarra = param_id_codbarra
              AND (param_fecha_inicial IS NULL OR P.fec_doc >= param_fecha_inicial)
              AND (param_fecha_final IS NULL OR P.fec_doc <= param_fecha_final)
            ORDER BY P.fec_doc, P.id_trans;
        END;
        $function$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION public.monitorstock_kardex(integer, integer, date, date);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_kardex(param_id_articulo integer, param_id_codbarra integer, param_fecha_inicial date, param_fecha_final date)
         RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer, bodega character varying, estado character varying, tipo_movimiento character varying, cantidad integer, vista character varying)
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                P.fec_doc,
                P.documento,
                P.nro_docum,
                COALESCE(B.nom_bodega, 'Sin Bodega')::character varying as bodega,
                COALESCE(E.cod_estado, '')::character varying as estado,
                CASE WHEN P.signo >= 0 THEN 'Entrada' ELSE 'Salida' END::character varying as tipo_movimiento,
                P.cantidad,
                P.vista
            FROM p_stock P
            LEFT JOIN m_bodegas B ON P.id_bodega = B.id
            LEFT JOIN m_estados E ON P.id_estado = E.id
            WHERE P.id_articulo = param_id_articulo
              AND P.id_codbarra = param_id_codbarra
              AND (param_fecha_inicial IS NULL OR P.fec_doc >= param_fecha_inicial)
              AND (param_fecha_final IS NULL OR P.fec_doc <= param_fecha_final)
            ORDER BY P.fec_doc, P.id_trans;
        END;
        $function$;
    """)
