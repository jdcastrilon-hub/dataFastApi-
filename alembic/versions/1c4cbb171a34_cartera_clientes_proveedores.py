"""cartera_clientes_proveedores

Revision ID: 1c4cbb171a34
Revises: f83a2ad17650
Create Date: 2026-08-29 16:28:31.556395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c4cbb171a34'
down_revision: Union[str, Sequence[str], None] = 'f83a2ad17650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ledgers de cartera (cuentas por cobrar/pagar), diseño acordado en
    # docs/tecnica/specs/tesoreria/cartera-y-cobranza.md. Mismo patron ya
    # usado en el proyecto para p_stock/s_stkbodegas y p_saldocliente/
    # s_saldocliente: p_ es el historico inmutable (un movimiento = una
    # fila, nunca se actualiza ni se borra), s_ es el snapshot (una fila
    # por titular con el saldo YA sumado), para no tener que hacer SUM
    # sobre el historico cada vez que se necesita saber cuanto debe/le
    # deben a un titular.
    #
    # Cartera clientes y cartera proveedores son tablas separadas (no un
    # tipo_titular generico) a proposito: son naturalezas contrarias
    # (activo vs. pasivo) y mezclarlas arriesga que un filtro olvidado en
    # un reporte junte lo que le deben a la empresa con lo que la empresa
    # debe - ver la spec para el detalle completo de esta decision.
    #
    # id_trans NO tiene default nextval: reutiliza el id_trans de la
    # transaccion que origina el movimiento (factura, pago, etc.), igual
    # que ya hace p_saldocliente - no genera numeracion propia. id_cliente/
    # id_proveedor sin FK real, mismo criterio que el resto de estas
    # tablas de ledger en el proyecto (t_facturas.id_turno, p_saldocliente.
    # id_cliente): se resuelven por join explicito, no por constraint.
    # fec_venc y documento_ref/nro_ref son nullable porque no todo
    # movimiento los necesita: fec_venc solo aplica al signo +1 (la deuda
    # que se origina, para poder calcular aging); documento_ref/nro_ref
    # solo al signo -1 (el abono/pago, para saber que documento especifico
    # esta cancelando).
    op.execute("""
        CREATE TABLE public.p_carteraclientes (
            id_trans        bigint NOT NULL,
            linea           integer NOT NULL DEFAULT 1,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente      integer NOT NULL,
            documento       varchar(16) NOT NULL,
            nro_docum       integer NOT NULL,
            documento_ref   varchar(16),
            nro_ref         integer,
            fec_doc         date NOT NULL,
            fec_venc        date,
            importe         numeric(14,2) NOT NULL,
            -- +1 factura a credito (aumenta la deuda); -1 abono/cobro
            -- (la cancela, total o parcialmente).
            signo           integer NOT NULL,
            vista           varchar(16) NOT NULL,
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, linea)
        )
    """)

    op.execute("""
        CREATE TABLE public.s_carteraclientes (
            id_emp      integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente  integer NOT NULL,
            saldo       numeric(14,2) NOT NULL DEFAULT 0,
            PRIMARY KEY (id_emp, id_cliente)
        )
    """)

    op.execute("""
        CREATE TABLE public.p_carteraproveedores (
            id_trans        bigint NOT NULL,
            linea           integer NOT NULL DEFAULT 1,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_proveedor    integer NOT NULL,
            documento       varchar(16) NOT NULL,
            nro_docum       integer NOT NULL,
            documento_ref   varchar(16),
            nro_ref         integer,
            fec_doc         date NOT NULL,
            fec_venc        date,
            importe         numeric(14,2) NOT NULL,
            -- +1 factura de compra a credito (aumenta la deuda); -1
            -- pago (la cancela, total o parcialmente).
            signo           integer NOT NULL,
            vista           varchar(16) NOT NULL,
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, linea)
        )
    """)

    op.execute("""
        CREATE TABLE public.s_carteraproveedores (
            id_emp        integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_proveedor  integer NOT NULL,
            saldo         numeric(14,2) NOT NULL DEFAULT 0,
            PRIMARY KEY (id_emp, id_proveedor)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS public.s_carteraproveedores")
    op.execute("DROP TABLE IF EXISTS public.p_carteraproveedores")
    op.execute("DROP TABLE IF EXISTS public.s_carteraclientes")
    op.execute("DROP TABLE IF EXISTS public.p_carteraclientes")
