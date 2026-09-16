"""facturas_observacion_nullable

Revision ID: 033b9788dd26
Revises: 5c374d540a8b
Create Date: 2026-08-14 19:34:30.509090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '033b9788dd26'
down_revision: Union[str, Sequence[str], None] = '5c374d540a8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # observacion era NOT NULL sin ningun default - venta-pos no la exige en el
    # formulario (venta-directa si, via Validators.required en el frontend, eso
    # no cambia), asi que POS no podia guardar sin escribir algo. Verificado
    # contra la BD real que ninguna funcion/vista/indice/trigger depende de que
    # sea NOT NULL antes de aplicar esto.
    op.alter_column('t_facturas', 'observacion', existing_type=sa.String(length=250), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('t_facturas', 'observacion', existing_type=sa.String(length=250), nullable=False)
