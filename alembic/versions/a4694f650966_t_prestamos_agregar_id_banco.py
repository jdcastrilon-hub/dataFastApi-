"""t_prestamos_agregar_id_banco

Revision ID: a4694f650966
Revises: 6ea8a86e351f
Create Date: 2026-08-30 11:34:55.424733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4694f650966'
down_revision: Union[str, Sequence[str], None] = '6ea8a86e351f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Correccion: el desembolso de un prestamo puede salir de una caja O de
    # un banco, igual que ya soporta p_movimientocajas (id_caja/id_banco
    # nullable, sp_caja_impacto_saldocaja decide con cual trabajar segun
    # cual de los dos venga lleno - ver ese SP en la BD real, esta tabla no
    # lo redefine, solo replica el mismo criterio de nullability). Se ajusta
    # aca en vez de reescribir la migracion anterior porque ya quedo
    # aplicada (aunque sin datos todavia).
    op.execute("ALTER TABLE public.t_prestamos ALTER COLUMN id_caja DROP NOT NULL")
    op.execute("""
        ALTER TABLE public.t_prestamos
        ADD COLUMN id_banco integer REFERENCES public.m_banco(id)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.t_prestamos DROP COLUMN id_banco")
    op.execute("ALTER TABLE public.t_prestamos ALTER COLUMN id_caja SET NOT NULL")
