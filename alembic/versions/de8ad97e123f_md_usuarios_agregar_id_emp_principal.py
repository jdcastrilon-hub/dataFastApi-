"""md_usuarios agregar id_emp_principal

Empresa que el sistema toma por defecto al loguear un usuario con acceso a
varias empresas (antes el login elegia con un .first() sin order_by, es decir
arbitrario). Nullable: el login cae al comportamiento anterior si esta en
NULL o si el usuario ya no tiene acceso activo a esa empresa (ver
controller_auth.py::login).

Revision ID: de8ad97e123f
Revises: 833750948175
Create Date: 2026-08-02 10:40:21.315305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de8ad97e123f'
down_revision: Union[str, Sequence[str], None] = '833750948175'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.md_usuarios ADD COLUMN id_emp_principal INTEGER NULL;")
    op.execute("ALTER TABLE public.md_usuarios ADD CONSTRAINT md_usuarios_id_emp_principal_fkey FOREIGN KEY (id_emp_principal) REFERENCES public.md_empresas(id_emp);")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.md_usuarios DROP CONSTRAINT md_usuarios_id_emp_principal_fkey;")
    op.execute("ALTER TABLE public.md_usuarios DROP COLUMN id_emp_principal;")
