"""agregar sp_general_control_costo: bloquear movimientos de articulos sin costo

Un articulo sin costo cargado (s_costoxbodegas.imp_costo_unitario = 0, o sin
fila) no se puede mover via ajuste/traslado - ninguno de los dos introduce
costo nuevo (ver docs/tecnica/specs/stock/ajuste-stock.md y
traslado-stock.md, seccion "Costo"), solo trasladan el costo ya existente.
Dejarlo pasar rompe el inventario valorado en silencio (queda a costo cero).

Se engancha en sp_general_control_transacciones (el mismo punto unico de
control ya usado para el chequeo de stock negativo), guardado por un
EXISTS sobre p_costos - solo corre si la transaccion realmente toco costo.
Como ajuste y traslado ya llaman este mismo wrapper, ambos quedan
protegidos sin tocarlos de nuevo. Un traslado dentro de la misma bodega
sigue sin tocar p_costos a proposito, asi que no dispara este control.

Revision ID: 5eed58b4477d
Revises: de8ad97e123f
Create Date: 2026-08-02 12:56:52.815951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5eed58b4477d'
down_revision: Union[str, Sequence[str], None] = 'de8ad97e123f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_general_control_costo(IN p_id_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        DECLARE
            v_id_articulo integer;
            v_cod_articulo character varying;
        BEGIN
            SELECT P.id_articulo, A.cod_articulo
            INTO v_id_articulo, v_cod_articulo
            FROM p_costos P
            LEFT JOIN m_articulos A ON A.id_articulo = P.id_articulo
            WHERE P.id_trans = p_id_trans
              AND P.imp_costo_unitario = 0
            LIMIT 1;

            IF v_id_articulo IS NOT NULL THEN
                RAISE EXCEPTION 'ERR_VAL: El articulo % (ID %) no tiene costo cargado. No se puede mover stock de un articulo sin costo, para no afectar el inventario valorado.', COALESCE(v_cod_articulo, '?'), v_id_articulo;
            END IF;
        END;
        $procedure$;
    """)

    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_general_control_transacciones(IN p_id_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            IF EXISTS (SELECT 1 FROM public.p_stock WHERE id_trans = p_id_trans) THEN
                CALL sp_general_control_stock(p_id_trans);
            END IF;

            IF EXISTS (SELECT 1 FROM public.p_costos WHERE id_trans = p_id_trans) THEN
                CALL sp_general_control_costo(p_id_trans);
            END IF;

            -- Puedes seguir anadiendo modulos aqui facilmente (sp_control_cartera, etc.)
        END;
        $procedure$;
    """)


def downgrade() -> None:
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_general_control_transacciones(IN p_id_trans integer)
         LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            IF EXISTS (SELECT 1 FROM public.p_stock WHERE id_trans = p_id_trans) THEN
                CALL sp_general_control_stock(p_id_trans);
            END IF;

            -- Puedes seguir anadiendo modulos aqui facilmente (sp_control_cartera, etc.)
        END;
        $procedure$;
    """)

    op.execute("DROP PROCEDURE IF EXISTS public.sp_general_control_costo(integer);")
