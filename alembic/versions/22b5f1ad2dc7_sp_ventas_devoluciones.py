"""sp_ventas_devoluciones

Revision ID: 22b5f1ad2dc7
Revises: a4579791d53f
Create Date: 2026-08-15 13:28:24.539471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22b5f1ad2dc7'
down_revision: Union[str, Sequence[str], None] = 'a4579791d53f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Mismo patron idempotente que sp_compras_devoluciones (DELETE+INSERT por
    # id_trans), pero signo +1: una nota credito es una ENTRADA a bodega (el
    # cliente devuelve mercancia), al reves de una devolucion a proveedor que
    # siempre es salida. documento_ref/nro_ref quedan apuntando a la factura
    # origen, para trazabilidad.
    #
    # A PROPOSITO no se toca p_costos todavia en este SP: la reversion de costo
    # (COGS) de una nota credito es una decision de negocio aparte (¿al costo
    # que tenia la venta original, o al costo promedio actual? - mismo tipo de
    # pregunta que motivo la correccion real de sp_comercial_ventapos este mismo
    # proyecto, un signo/valor mal puesto ahi corrompe el costo promedio en
    # silencio) - se conecta en una migracion separada junto con el saldo a favor
    # y el GastoCaja, no aca.
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_ventas_devoluciones(
            IN operacion character varying,
            IN parm_trans integer,
            IN p_usuario character varying DEFAULT NULL::character varying)
        LANGUAGE plpgsql
        AS $procedure$
        BEGIN
            DELETE FROM p_stock WHERE id_trans = parm_trans;

            INSERT INTO p_stock
            SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
                   B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
                   B.cantidad, 1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod
            FROM t_notafactura A
            INNER JOIN td_notafactura B ON A.id_trans = B.id_trans
            INNER JOIN t_facturas C ON A.id_trans_ref = C.id_trans AND A.id_emp = C.id_emp
            WHERE A.id_trans = parm_trans;
        END;
        $procedure$
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP PROCEDURE IF EXISTS public.sp_ventas_devoluciones(character varying, integer, character varying)")
