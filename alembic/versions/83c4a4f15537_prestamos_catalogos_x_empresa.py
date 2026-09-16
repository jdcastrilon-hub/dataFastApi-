"""prestamos_catalogos_x_empresa

Revision ID: 83c4a4f15537
Revises: 3407d2f8e14f
Create Date: 2026-08-30 13:48:56.461596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83c4a4f15537'
down_revision: Union[str, Sequence[str], None] = '3407d2f8e14f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Modulo Prestamos: m_periodicidad y m_formulaprestamo son catalogos
    # GLOBALES (un solo universo para toda la plataforma, se mantienen a nivel
    # plataforma), pero cada empresa solo debe ver/usar un subconjunto - un
    # negocio que solo presta mensual no quiere ver semanal/quincenal, ni todas
    # las formulas que existan. Estas dos tablas puente son el opt-in por
    # empresa.
    #
    # Presencia de la fila = habilitado. A diferencia de md_empresaxmodulo (que
    # lleva `activo` boolean y togglea sin borrar), aqui se usa el patron
    # borrar-e-reinsertar de m_confcomercial: la pantalla "Configuracion de
    # Prestamos" guarda la grilla completa en una sola llamada, asi que solo se
    # almacenan los items activos y no hace falta columna `activo`.
    #
    # Las empresas existentes arrancan VACIAS (opt-in explicito): no se siembra
    # ningun default. El formulario de Prestamo no dejara originar mientras la
    # empresa no tenga >=1 periodicidad y >=1 formula asignadas.
    op.execute("""
        CREATE TABLE public.m_periodicidadxempresa (
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_periodicidad integer NOT NULL REFERENCES public.m_periodicidad(id),
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_emp, id_periodicidad)
        )
    """)
    op.execute("""
        CREATE TABLE public.m_formulaprestamoxempresa (
            id_emp     integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_formula integer NOT NULL REFERENCES public.m_formulaprestamo(id),
            fecha_mod  timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_emp, id_formula)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS public.m_formulaprestamoxempresa")
    op.execute("DROP TABLE IF EXISTS public.m_periodicidadxempresa")
