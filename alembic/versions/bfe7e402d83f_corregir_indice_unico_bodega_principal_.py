"""corregir indice unico bodega principal por sucursal (SI/boolean)

El indice parcial ux_bodega_principal_por_sucursal (una bodega principal
activa por sucursal) llevaba tiempo sin bloquear nada, por dos motivos
acumulados, ninguno de esta sesion de bodegas:
1. Su condicion comparaba principal = 'S', pero el dato real siempre fue
   'SI'/'NO' (nunca 'S'/'N') - nunca coincidio.
2. La migracion 833750948175 (activo varchar->boolean) corrigio el trigger
   de limite de plan pero no toco este indice - activo = 'S' comparado
   contra boolean tampoco coincidio nunca desde ese cambio.

Encontrado en vivo 2026-08-07: empresa 1/sucursal 1 llego a tener 3 bodegas
con principal='SI' activo=true simultaneamente sin que la BD lo impidiera.
Se confirmo con el usuario mantener el alcance ORIGINAL (por sucursal, no
por empresa completa) - una empresa con varias sucursales puede seguir
teniendo una bodega principal por cada una.

Revision ID: bfe7e402d83f
Revises: ba7abfa79763
Create Date: 2026-08-07 09:21:22.992577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfe7e402d83f'
down_revision: Union[str, Sequence[str], None] = 'ba7abfa79763'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP INDEX IF EXISTS public.ux_bodega_principal_por_sucursal;")
    op.execute("""
        CREATE UNIQUE INDEX ux_bodega_principal_por_sucursal
        ON public.m_bodegas (id_sucursal)
        WHERE (principal = 'SI' AND activo = true);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS public.ux_bodega_principal_por_sucursal;")
    op.execute("""
        CREATE UNIQUE INDEX ux_bodega_principal_por_sucursal
        ON public.m_bodegas (id_sucursal)
        WHERE ((principal)::text = 'S'::text AND (activo)::text = 'S'::text);
    """)
