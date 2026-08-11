"""m_bodegas agregar id_emp para autonumeracion por empresa

m_bodegas no tenia columna id_emp propia (la empresa se alcanzaba
indirectamente via sucursal.id_emp), y su restriccion de unicidad de
cod_bodega era por sucursal, no por empresa. Requisito previo del proceso
docs/tecnica/specs/core/autonumeracion-catalogos.md (piloto: Bodegas) para
poder pedir el consecutivo via md_numeradores con clave (id_emp, "BODEGA").

Revision ID: ba7abfa79763
Revises: 32eb6e603dcd
Create Date: 2026-08-06 21:21:33.014937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba7abfa79763'
down_revision: Union[str, Sequence[str], None] = '32eb6e603dcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.m_bodegas ADD COLUMN id_emp INTEGER NULL;")
    op.execute("""
        UPDATE public.m_bodegas b
        SET id_emp = s.id_emp
        FROM public.m_sucursales s
        WHERE b.id_sucursal = s.id;
    """)
    op.execute("ALTER TABLE public.m_bodegas ALTER COLUMN id_emp SET NOT NULL;")
    op.execute("ALTER TABLE public.m_bodegas ADD CONSTRAINT m_bodegas_id_emp_fkey FOREIGN KEY (id_emp) REFERENCES public.md_empresas(id_emp);")

    op.execute("ALTER TABLE public.m_bodegas DROP CONSTRAINT m_bodegas_unique;")
    op.execute("ALTER TABLE public.m_bodegas ADD CONSTRAINT m_bodegas_unique UNIQUE (id_emp, cod_bodega);")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.m_bodegas DROP CONSTRAINT m_bodegas_unique;")
    op.execute("ALTER TABLE public.m_bodegas ADD CONSTRAINT m_bodegas_unique UNIQUE (id_sucursal, cod_bodega);")

    op.execute("ALTER TABLE public.m_bodegas DROP CONSTRAINT m_bodegas_id_emp_fkey;")
    op.execute("ALTER TABLE public.m_bodegas DROP COLUMN id_emp;")
