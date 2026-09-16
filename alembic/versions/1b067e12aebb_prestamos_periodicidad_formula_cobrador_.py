"""prestamos_periodicidad_formula_cobrador_moneda

Revision ID: 1b067e12aebb
Revises: a4694f650966
Create Date: 2026-08-30 12:40:42.522436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b067e12aebb'
down_revision: Union[str, Sequence[str], None] = 'a4694f650966'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # m_periodicidad: catalogo global (sin id_emp, mismo criterio que
    # m_costeo) en vez de campo abierto - el usuario podia escribir
    # "mensual"/"mensuaal"/etc. y td_prestamos.fec_venc depende de este
    # valor para calcular vencimientos, no es un dato cosmetico.
    op.execute("""
        CREATE TABLE public.m_periodicidad (
            id          SERIAL PRIMARY KEY,
            codigo      varchar(20) NOT NULL,
            nombre      varchar(50) NOT NULL,
            dias        integer NOT NULL,
            activo      boolean NOT NULL DEFAULT true,
            fecha_mod   timestamp DEFAULT now(),
            CONSTRAINT m_periodicidad_unique UNIQUE (codigo)
        )
    """)
    op.execute("""
        INSERT INTO public.m_periodicidad (codigo, nombre, dias) VALUES
            ('DIARIA', 'Diaria', 1),
            ('SEMANAL', 'Semanal', 7),
            ('QUINCENAL', 'Quincenal', 15),
            ('MENSUAL', 'Mensual', 30),
            ('BIMESTRAL', 'Bimestral', 60)
    """)

    # m_formulaprestamo: catalogo global de formulas de calculo de cuota.
    # A diferencia de m_costeo (que existe pero ningun codigo lo consulta),
    # esta si debe quedar conectada a una funcion real que ramifique sobre
    # `codigo` al calcular valor_cuota/cronograma - ver
    # docs/tecnica/specs/prestamos/prestamos.md.
    #
    # genera_interes_mora: no es una decision por empresa (una misma empresa
    # puede prestar comercialmente Y prestarle a un familiar al 0%) - vive
    # en la formula elegida por CADA prestamo. Columna agregada ahora sin
    # logica de mora implementada todavia (fuera de alcance de esta fase),
    # para no tener que migrar la tabla otra vez cuando se construya.
    op.execute("""
        CREATE TABLE public.m_formulaprestamo (
            id                      SERIAL PRIMARY KEY,
            codigo                  varchar(30) NOT NULL,
            nombre                  varchar(80) NOT NULL,
            genera_interes_mora     boolean NOT NULL DEFAULT false,
            activo                  boolean NOT NULL DEFAULT true,
            fecha_mod               timestamp DEFAULT now(),
            CONSTRAINT m_formulaprestamo_unique UNIQUE (codigo)
        )
    """)
    op.execute("""
        INSERT INTO public.m_formulaprestamo (codigo, nombre, genera_interes_mora) VALUES
            ('FIJO_CAPITAL_ORIGINAL', 'Cuota fija sobre capital original (capital/N + capital*tasa)', false)
    """)

    # t_prestamos: periodicidad e id_formula obligatorios (tabla vacia
    # todavia, seguro agregarlos NOT NULL sin default). id_cobrador nullable
    # (usuario real del sistema, md_usuarios - un prestamo puede no tener
    # cobrador asignado). id_moneda nullable y SIN fk todavia: no existe
    # m_moneda en el proyecto (t_facturas.id_moneda tiene el mismo problema -
    # columna sin catalogo real detras), se deja mapeada para cuando se
    # diseñe moneda de forma transversal, no soluciona el problema aqui.
    op.execute("""
        ALTER TABLE public.t_prestamos
        ADD COLUMN id_periodicidad integer NOT NULL REFERENCES public.m_periodicidad(id),
        ADD COLUMN id_formula integer NOT NULL REFERENCES public.m_formulaprestamo(id),
        ADD COLUMN id_cobrador integer REFERENCES public.md_usuarios(id_usuario),
        ADD COLUMN id_moneda integer
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE public.t_prestamos
        DROP COLUMN id_moneda,
        DROP COLUMN id_cobrador,
        DROP COLUMN id_formula,
        DROP COLUMN id_periodicidad
    """)
    op.execute("DROP TABLE IF EXISTS public.m_formulaprestamo")
    op.execute("DROP TABLE IF EXISTS public.m_periodicidad")
