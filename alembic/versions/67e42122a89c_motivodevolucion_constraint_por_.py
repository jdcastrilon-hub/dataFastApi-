"""m_motivodevolucion: cod_motivo global -> por empresa

Paso 2 del proceso de autonumeracion de catalogos (ver
docs/tecnica/specs/core/autonumeracion-catalogos.md), mismo tratamiento que
ya se aplico a m_estados/m_motivoajuste en la migracion 3dd4a4c32d50: el
cod_motivo de Motivos de Devolucion era unico a nivel global
(m_motivodevolucion_unique UNIQUE(cod_motivo)), pasa a ser unico por
empresa, requisito para poder numerar con md_numeradores (contador
independiente por id_emp).

Revision ID: 67e42122a89c
Revises: 62ad1ce865e7
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67e42122a89c'
down_revision: Union[str, Sequence[str], None] = '62ad1ce865e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.m_motivodevolucion DROP CONSTRAINT m_motivodevolucion_unique;")
    op.execute("ALTER TABLE public.m_motivodevolucion ADD CONSTRAINT m_motivodevolucion_unique UNIQUE (id_emp, cod_motivo);")


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_motivodevolucion DROP CONSTRAINT m_motivodevolucion_unique;")
    op.execute("ALTER TABLE public.m_motivodevolucion ADD CONSTRAINT m_motivodevolucion_unique UNIQUE NULLS DISTINCT (cod_motivo);")
