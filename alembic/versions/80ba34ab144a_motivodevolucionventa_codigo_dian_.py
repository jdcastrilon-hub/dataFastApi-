"""motivodevolucionventa_codigo_dian_afecta_stock

Revision ID: 80ba34ab144a
Revises: 22b5f1ad2dc7
Create Date: 2026-08-22 15:46:25.656198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80ba34ab144a'
down_revision: Union[str, Sequence[str], None] = '22b5f1ad2dc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # codigo_dian: referencia al concepto oficial de nota credito/debito de la
    # DIAN (1-6, ver Anexo Tecnico Factura Electronica v1.9, 13.2.7.4/13.2.7.5) -
    # todavia no se emite factura electronica, asi que queda nullable y sin
    # logica propia por ahora; es solo para no tener que migrar de nuevo cuando
    # se conecte la facturacion electronica. Un motivo puede no mapear a un
    # codigo fijo (ej. "Ajuste de Valor" cubre los conceptos 3 y 4 a la vez -
    # se decide cual de los dos aplica recien al emitir la nota electronica).
    #
    # afecta_stock: si la nota con este motivo reingresa mercancia fisica a
    # bodega o es un ajuste puramente de valor (sin movimiento de inventario).
    # Eje independiente de devuelve_dinero (ese decide de donde sale el dinero,
    # este decide si hay mercancia de por medio).
    op.execute("""
        ALTER TABLE public.m_motivodevolucionventa
            ADD COLUMN codigo_dian integer,
            ADD COLUMN afecta_stock boolean NOT NULL DEFAULT true
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE public.m_motivodevolucionventa
            DROP COLUMN IF EXISTS afecta_stock,
            DROP COLUMN IF EXISTS codigo_dian
    """)
