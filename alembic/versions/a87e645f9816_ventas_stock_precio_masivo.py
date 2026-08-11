"""ventas: funcion stock+precio masivo (recalculo al cambiar bodega/estado/lista)

Revision ID: a87e645f9816
Revises: c83efc0e4854
Create Date: 2026-08-10 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a87e645f9816'
down_revision = 'c83efc0e4854'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION public.ventas_obtener_stock_precio_masivo(
            p_cadena_articulos text,
            p_id_bodega integer,
            p_id_estado integer,
            p_id_lista integer DEFAULT 0
        )
        RETURNS TABLE(idarticulo integer, idcodbarra integer, stock integer, precio numeric, idimpuesto integer, porcentaje numeric)
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN QUERY
            -- select * from ventas_obtener_stock_precio_masivo('10-17;4-5', 1, 1, 7)

            WITH Items_Separados AS (
                SELECT string_to_table(p_cadena_articulos, ';') AS pareja
            ),
            Items_Parsed AS (
                SELECT
                    split_part(pareja, '-', 1)::INTEGER AS v_id_art,
                    split_part(pareja, '-', 2)::INTEGER AS v_id_cod
                FROM Items_Separados
                WHERE pareja <> ''
            )
            SELECT
                A.v_id_art,
                A.v_id_cod,
                COALESCE(B.cantidad, 0)::INTEGER AS stock,
                -- Mismo criterio de resolucion de precio que ventadisponiblexbodega:
                -- primero la lista pedida, si no tiene precio cae a la general activa
                -- de la empresa duena del articulo.
                COALESCE(
                    (SELECT S.precio_venta FROM s_precioxarticulo S
                     WHERE S.id_lista = p_id_lista AND S.id_articulo = A.v_id_art),
                    (SELECT S2.precio_venta FROM s_precioxarticulo S2
                     INNER JOIN m_listaprecio L ON L.id_lista = S2.id_lista
                     INNER JOIN m_articulos AR ON AR.id_articulo = S2.id_articulo
                     WHERE S2.id_articulo = A.v_id_art
                       AND L.es_general = true AND L.activo = true
                       AND L.id_emp = AR.id_emp),
                    0
                )::NUMERIC AS precio,
                COALESCE(M.id_impuesto, 0)::INTEGER AS idimpuesto,
                COALESCE(IMP.porc_tasa, 0)::NUMERIC AS porcentaje
            FROM Items_Parsed A
            LEFT JOIN s_stkbodegas B ON B.id_bodega = p_id_bodega AND B.id_estado = p_id_estado
                AND B.id_articulo = A.v_id_art AND B.id_codbarra = A.v_id_cod
            LEFT JOIN m_articulos M ON M.id_articulo = A.v_id_art
            LEFT JOIN m_impuesto IMP ON IMP.id = M.id_impuesto;
        END;
        $function$
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.ventas_obtener_stock_precio_masivo(text, integer, integer, integer)")
