"""m_proveedores: agregar responsable_iva

Nuevo atributo tributario del proveedor, independiente de `regimen`
(Ordinario/Simple es el regimen de renta; responsable_iva es un eje aparte -
un proveedor puede ser Regimen Simple y aun asi ser responsable de IVA, o
viceversa). Default false (No responsable) para las filas existentes y para
cualquier registro nuevo que no lo indique explicitamente.

Revision ID: f83a2ad17650
Revises: facf6f05ef0c
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f83a2ad17650'
down_revision: Union[str, Sequence[str], None] = 'facf6f05ef0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.m_proveedores ADD COLUMN responsable_iva BOOLEAN NOT NULL DEFAULT false;")


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_proveedores DROP COLUMN responsable_iva;")
