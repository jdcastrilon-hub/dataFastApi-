"""t_prestamos_td_prestamos

Revision ID: 6ea8a86e351f
Revises: 1c4cbb171a34
Create Date: 2026-08-30 11:17:14.976310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ea8a86e351f'
down_revision: Union[str, Sequence[str], None] = '1c4cbb171a34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Modulo Prestamos, diseno acordado en
    # docs/tecnica/specs/prestamos/prestamos.md. t_prestamos es la cabecera
    # del contrato (capital, plazo, tasa, cuota ya calculada y guardada -
    # nunca se recalcula despues aunque cambie algo mas adelante).
    #
    # id_trans SI tiene default nextval('id_transaccion') a diferencia de
    # p_carteraclientes: aca es la transaccion que ORIGINA el movimiento
    # (mismo criterio que t_facturas), no un movimiento que reutiliza el
    # id_trans de otra tabla. id_cliente sin FK real, mismo criterio que el
    # resto de tablas de cartera del proyecto (se resuelve por join
    # explicito). id_caja/id_mediopago si llevan FK real porque el
    # desembolso escribe un egreso real en p_movimientocajas (mismas FKs
    # que ya usa esa tabla).
    #
    # documento_ref/nro_ref son nullable: solo se llenan cuando el prestamo
    # nace de un retanqueo, para trazar a que contrato viejo reemplaza.
    op.execute("""
        CREATE TABLE public.t_prestamos (
            id_trans        bigint DEFAULT nextval('id_transaccion'::regclass) NOT NULL,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente      integer NOT NULL,
            documento       varchar(16) NOT NULL DEFAULT 'PRESTAMO',
            nro_docum       integer NOT NULL,
            documento_ref   varchar(16),
            nro_ref         integer,
            fec_desembolso  date NOT NULL,
            fec_fin         date NOT NULL,
            capital         numeric(14,2) NOT NULL,
            num_cuotas      integer NOT NULL,
            tasa_pct        numeric(5,2) NOT NULL,
            valor_cuota     numeric(14,2) NOT NULL,
            id_caja         integer NOT NULL REFERENCES public.m_cajas(id),
            id_mediopago    integer NOT NULL REFERENCES public.m_mediopagos(id),
            -- ACTIVO / CANCELADO / RETANQUEADO
            id_estado       varchar(20) NOT NULL DEFAULT 'ACTIVO',
            observacion     varchar(250),
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            logs            json,
            PRIMARY KEY (id_trans),
            CONSTRAINT t_prestamos_nro_docum_unique UNIQUE (id_emp, nro_docum)
        )
    """)

    # td_prestamos es el cronograma de cuotas: mutable a proposito (a
    # diferencia de p_carteraclientes, que es historico inmutable), para que
    # ajuste de cuotas pueda reprogramar fec_venc/valor_cuota de cuotas
    # futuras sin tener que escribir reversiones en el ledger de dinero.
    # linea = numero de cuota dentro del contrato (1..N). Mismo patron ya
    # usado por td_cierreturno (detalle transaccional separado del ledger).
    op.execute("""
        CREATE TABLE public.td_prestamos (
            id_trans        bigint NOT NULL REFERENCES public.t_prestamos(id_trans),
            linea           integer NOT NULL,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            valor_cuota     numeric(14,2) NOT NULL,
            fec_venc        date NOT NULL,
            saldo_cuota     numeric(14,2) NOT NULL,
            -- PENDIENTE / PARCIAL / PAGADA / ANULADA
            id_estado       varchar(20) NOT NULL DEFAULT 'PENDIENTE',
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, linea)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS public.td_prestamos")
    op.execute("DROP TABLE IF EXISTS public.t_prestamos")
