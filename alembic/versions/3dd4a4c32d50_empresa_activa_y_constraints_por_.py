"""empresa activa y constraints por-empresa en estados-motivoajuste-tiposervicio

Revision ID: 3dd4a4c32d50
Revises: 1440d4dea6ae
Create Date: 2026-08-01 15:34:22.645259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dd4a4c32d50'
down_revision: Union[str, Sequence[str], None] = '1440d4dea6ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # md_empresas.activa - bloqueo comercial de empresa completa
    op.execute("ALTER TABLE public.md_empresas ADD COLUMN activa BOOLEAN NOT NULL DEFAULT TRUE;")

    # m_estados: cod_estado global -> por empresa
    op.execute("ALTER TABLE public.m_estados DROP CONSTRAINT m_estados_unique;")
    op.execute("ALTER TABLE public.m_estados ADD CONSTRAINT m_estados_unique UNIQUE (id_emp, cod_estado);")

    # m_motivoajuste: cod_motivo global -> por empresa
    op.execute("ALTER TABLE public.m_motivoajuste DROP CONSTRAINT m_motivoajuste_unique;")
    op.execute("ALTER TABLE public.m_motivoajuste ADD CONSTRAINT m_motivoajuste_unique UNIQUE (id_emp, cod_motivo);")

    # m_tiposervicio: no tenia ninguna constraint sobre cod_servicio
    op.execute("ALTER TABLE public.m_tiposervicio ADD CONSTRAINT m_tiposervicio_id_emp_cod_servicio_key UNIQUE (id_emp, cod_servicio);")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.m_tiposervicio DROP CONSTRAINT m_tiposervicio_id_emp_cod_servicio_key;")

    op.execute("ALTER TABLE public.m_motivoajuste DROP CONSTRAINT m_motivoajuste_unique;")
    op.execute("ALTER TABLE public.m_motivoajuste ADD CONSTRAINT m_motivoajuste_unique UNIQUE NULLS DISTINCT (cod_motivo);")

    op.execute("ALTER TABLE public.m_estados DROP CONSTRAINT m_estados_unique;")
    op.execute("ALTER TABLE public.m_estados ADD CONSTRAINT m_estados_unique UNIQUE NULLS DISTINCT (cod_estado);")

    op.execute("ALTER TABLE public.md_empresas DROP COLUMN activa;")
