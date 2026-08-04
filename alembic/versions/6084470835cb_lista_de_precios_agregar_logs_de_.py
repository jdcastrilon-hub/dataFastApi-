"""lista de precios: agregar logs de auditoria

Se me paso agregar el campo "logs" (jsonb de auditoria, patron {operacion,
usuario_mod, fecha_mod}) en m_listaprecio y m_reglaprecio - son maestros m_,
deberian tenerlo igual que el resto (m_articulos, m_categorias, etc.). No
aplica a m_listaprecioxuser (tabla de permiso pura, sin logs, igual que
md_usuario_permiso/md_rolxpermiso).

Revision ID: 6084470835cb
Revises: 9c8225580f88
Create Date: 2026-07-28 21:12:59.065401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6084470835cb'
down_revision: Union[str, Sequence[str], None] = '9c8225580f88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.m_listaprecio ADD COLUMN logs JSON NULL;")
    op.execute("ALTER TABLE public.m_reglaprecio ADD COLUMN logs JSON NULL;")


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_reglaprecio DROP COLUMN logs;")
    op.execute("ALTER TABLE public.m_listaprecio DROP COLUMN logs;")
