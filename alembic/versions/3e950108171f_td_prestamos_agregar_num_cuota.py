"""td_prestamos_agregar_num_cuota

Revision ID: 3e950108171f
Revises: 1b067e12aebb
Create Date: 2026-08-30 12:49:45.629000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e950108171f'
down_revision: Union[str, Sequence[str], None] = '1b067e12aebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # linea (parte de la PK compuesta id_trans+linea) es identidad estable
    # de fila, nunca se reutiliza. num_cuota es la posicion logica visible
    # ("cuota X de N") - pueden divergir despues de un ajuste de cuotas que
    # anule una fila y cree su reemplazo (el reemplazo recibe un linea
    # nuevo, pero conceptualmente sigue siendo la misma cuota N). Al
    # desembolsar, para las cuotas originales, linea y num_cuota nacen
    # iguales.
    op.execute("""
        ALTER TABLE public.td_prestamos
        ADD COLUMN num_cuota integer NOT NULL
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.td_prestamos DROP COLUMN num_cuota")
