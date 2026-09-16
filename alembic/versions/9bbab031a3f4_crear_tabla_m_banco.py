"""crear tabla m_banco

Catalogo de bancos por empresa (no global) - cada empresa puede usar bancos
distintos, asi que UNIQUE(id_emp, cod_banco) en vez de un cod_banco unico a
nivel de toda la plataforma. Mismo patron que m_sucursales/m_negocios.

Revision ID: 9bbab031a3f4
Revises: 8106e0420f06
Create Date: 2026-08-11 19:29:40.437766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bbab031a3f4'
down_revision: Union[str, Sequence[str], None] = '8106e0420f06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE public.m_banco (
            id SERIAL PRIMARY KEY,
            id_emp INTEGER NOT NULL REFERENCES public.md_empresas(id_emp),
            cod_banco VARCHAR(10) NOT NULL,
            nom_banco VARCHAR(100) NOT NULL,
            activo BOOLEAN NOT NULL DEFAULT true,
            logs JSON,
            fecha_mod TIMESTAMP,
            CONSTRAINT m_banco_unique UNIQUE (id_emp, cod_banco)
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE public.m_banco;")
