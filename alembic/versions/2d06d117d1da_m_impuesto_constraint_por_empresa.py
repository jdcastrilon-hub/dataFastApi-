"""m_impuesto: tasa_impu de (id_tipo, tasa_impu) global a (id_emp, tasa_impu)

Paso 3 del proceso de autonumeracion de catalogos (ver
docs/tecnica/specs/core/autonumeracion-catalogos.md, seccion "Impuestos -
caso especial"): la restriccion hoy es UniqueConstraint('id_tipo',
'tasa_impu') - ni siquiera esta scopeada por empresa, pese a que Impuesto ya
tiene columna id_emp. Se simplifica a UniqueConstraint('id_emp',
'tasa_impu') - un solo consecutivo por empresa para todo el catalogo de
Impuestos, sin sub-numerar por tipo de impuesto, mismo criterio que el resto
de catalogos de este proceso. Mismo nombre de constraint conservado.

Revision ID: 2d06d117d1da
Revises: 67e42122a89c
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d06d117d1da'
down_revision: Union[str, Sequence[str], None] = '67e42122a89c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.m_impuesto DROP CONSTRAINT impuestos_pk_unic;")
    op.execute("ALTER TABLE public.m_impuesto ADD CONSTRAINT impuestos_pk_unic UNIQUE (id_emp, tasa_impu);")


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_impuesto DROP CONSTRAINT impuestos_pk_unic;")
    op.execute("ALTER TABLE public.m_impuesto ADD CONSTRAINT impuestos_pk_unic UNIQUE (id_tipo, tasa_impu);")
