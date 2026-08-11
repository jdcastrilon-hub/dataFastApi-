"""ventas: id_lista en t_facturas y precio real en ventadisponiblexbodega

Cierra el hueco encontrado el 2026-08-08 al analizar el modulo de precios:
ventadisponiblexbodega() (usada tanto por venta-directa como por venta-pos
via GET /core/services/ini/ventaDisponiblexBodega) tenia el precio
hardcodeado en 200 para TODO articulo, sin usar nunca s_precioxarticulo. Este
pase agrega la columna que persiste que lista se uso en cada venta y hace que
la funcion resuelva el precio real, con fallback a la lista general de la
empresa cuando la lista pedida no tiene precio para ese articulo.

Alcance deliberadamente acotado (confirmado con el usuario): solo venta-directa
gana el selector de lista en el encabezado. La resolucion por listas propias
del cliente (ver project_data_lista_precios_design) sigue sin construirse -
esto es el paso "sacar el 200 harcodeado + lista general real", no el diseño
completo.

Revision ID: 88cf09a12635
Revises: 59f2dd3c893f
Create Date: 2026-08-09 16:48:42.302357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88cf09a12635'
down_revision: Union[str, Sequence[str], None] = '59f2dd3c893f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nullable: ventas historicas (y las que se hagan sin tocar el selector
    # nuevo) no tienen lista asociada - mismo criterio ya usado para id_turno/id_caja.
    op.execute("ALTER TABLE public.t_facturas ADD COLUMN id_lista integer NULL;")

    # Signature vieja tenia 4 parametros - hay que dropearla antes de crear la
    # nueva de 5 (Postgres no permite cambiar la firma con CREATE OR REPLACE).
    op.execute("DROP FUNCTION IF EXISTS public.ventadisponiblexbodega(integer, integer, integer, integer);")

    op.execute("""
        CREATE OR REPLACE FUNCTION public.ventadisponiblexbodega(
            param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer,
            param_estado_id integer, param_id_lista integer DEFAULT 0)
        RETURNS TABLE(stock integer, precio numeric, impuesto integer, porcentaje numeric)
        LANGUAGE plpgsql
        AS $function$

        DECLARE
            v_stock integer;
            v_precio numeric(20,2);
            v_impuesto integer;
            v_porcentaje numeric;
        BEGIN

            select cantidad from s_stkbodegas INTO v_stock
            where id_bodega=param_bodega_id
            and id_estado=param_estado_id
            and id_articulo=param_articulo_id
            and id_codbarra=param_id_codbarra;

            select id_impuesto,B.porc_tasa from m_articulos A
            inner join m_impuesto B on A.id_impuesto=B.id
            INTO v_impuesto,v_porcentaje
            where id_articulo=param_articulo_id;

            -- Precio real: primero intenta la lista pedida (si vino alguna,
            -- 0 = ninguna todavia resuelta por el llamador); si esa lista no
            -- tiene precio cargado para el articulo, cae a la lista general
            -- activa de la empresa duena del articulo (m_articulos.id_emp).
            IF param_id_lista > 0 THEN
                SELECT precio_venta INTO v_precio
                FROM s_precioxarticulo
                WHERE id_lista = param_id_lista AND id_articulo = param_articulo_id;
            END IF;

            IF v_precio IS NULL THEN
                SELECT S.precio_venta INTO v_precio
                FROM s_precioxarticulo S
                INNER JOIN m_listaprecio L ON L.id_lista = S.id_lista
                INNER JOIN m_articulos A ON A.id_articulo = S.id_articulo
                WHERE S.id_articulo = param_articulo_id
                  AND L.es_general = true AND L.activo = true
                  AND L.id_emp = A.id_emp;
            END IF;

            RETURN QUERY
            SELECT
                COALESCE(v_stock, 0),
                COALESCE(v_precio, 0),
                COALESCE(v_impuesto, 0),
                COALESCE(v_porcentaje, 0);

        END
        $function$;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.ventadisponiblexbodega(integer, integer, integer, integer, integer);")

    op.execute("""
        CREATE OR REPLACE FUNCTION public.ventadisponiblexbodega(
            param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer, param_estado_id integer)
        RETURNS TABLE(stock integer, precio numeric, impuesto integer, porcentaje numeric)
        LANGUAGE plpgsql
        AS $function$

        DECLARE
            v_stock integer;
            v_precio numeric(20,2);
            v_impuesto integer;
            v_porcentaje numeric;
        BEGIN

            select cantidad from s_stkbodegas INTO v_stock
            where id_bodega=param_bodega_id
            and id_estado=param_estado_id
            and id_articulo=param_articulo_id
            and id_codbarra=param_id_codbarra;

            select id_impuesto,B.porc_tasa from m_articulos A
            inner join m_impuesto B on A.id_impuesto=B.id
            INTO v_impuesto,v_porcentaje
            where id_articulo=param_articulo_id;

            v_precio := 200;

            RETURN QUERY
            SELECT
                COALESCE(v_stock, 0),
                COALESCE(v_precio, 0),
                COALESCE(v_impuesto, 0),
                COALESCE(v_porcentaje, 0);

        END
        $function$;
    """)

    op.execute("ALTER TABLE public.t_facturas DROP COLUMN IF EXISTS id_lista;")
