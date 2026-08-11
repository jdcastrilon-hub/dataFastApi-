"""md_rol agregar es_protegido

Flag para el rol "Admin" que ahora crea automaticamente el provisioning de
empresa (junto al ya existente SUPERADMIN) - impide borrarlo desde
delete_rol. Deliberadamente NO expuesto en el payload de escritura de
RolCreate (create_rol/update_rol nunca lo asignan desde obj), mismo criterio
que ya usa es_superadmin: se puede LEER (para que el frontend esconda el
boton de eliminar) pero no se puede escribir vía la pantalla de Roles.

Revision ID: 192abea6d48d
Revises: c5d5b0d0de6a
Create Date: 2026-08-04 18:02:05.563442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '192abea6d48d'
down_revision: Union[str, Sequence[str], None] = 'c5d5b0d0de6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.md_rol ADD COLUMN es_protegido BOOLEAN NOT NULL DEFAULT false;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.md_rol DROP COLUMN es_protegido;")
