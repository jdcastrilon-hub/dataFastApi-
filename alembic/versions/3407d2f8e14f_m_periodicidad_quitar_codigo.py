"""m_periodicidad_quitar_codigo

Revision ID: 3407d2f8e14f
Revises: 3e950108171f
Create Date: 2026-08-30 13:08:05.800860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3407d2f8e14f'
down_revision: Union[str, Sequence[str], None] = '3e950108171f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # codigo era texto duplicado de nombre (ej. codigo='MENSUAL',
    # nombre='Mensual') sin ningun uso real: lo unico que la logica de
    # calculo necesita es `dias`, codigo/nombre son solo para el combo del
    # usuario. Se quita codigo, se deja nombre como unico texto visible +
    # observacion opcional. Distinto de m_formulaprestamo.codigo, que si es
    # operativo (una funcion futura ramifica sobre ese valor) - no se toca.
    op.execute("ALTER TABLE public.m_periodicidad DROP CONSTRAINT m_periodicidad_unique")
    op.execute("ALTER TABLE public.m_periodicidad DROP COLUMN codigo")
    op.execute("""
        ALTER TABLE public.m_periodicidad
        ADD COLUMN observacion varchar(250),
        ADD CONSTRAINT m_periodicidad_nombre_unique UNIQUE (nombre)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.m_periodicidad DROP CONSTRAINT m_periodicidad_nombre_unique")
    op.execute("ALTER TABLE public.m_periodicidad DROP COLUMN observacion")
    op.execute("ALTER TABLE public.m_periodicidad ADD COLUMN codigo varchar(20)")
    op.execute("UPDATE public.m_periodicidad SET codigo = upper(nombre)")
    op.execute("ALTER TABLE public.m_periodicidad ALTER COLUMN codigo SET NOT NULL")
    op.execute("ALTER TABLE public.m_periodicidad ADD CONSTRAINT m_periodicidad_unique UNIQUE (codigo)")
