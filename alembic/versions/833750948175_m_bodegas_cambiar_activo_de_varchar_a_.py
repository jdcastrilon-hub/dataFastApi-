"""m_bodegas: cambiar activo de varchar a boolean

Tambien corrige el trigger trg_m_bodegas_validar_limite_plan
(m_bodegas_validar_limite_plan()), que comparaba NEW.activo/b.activo contra
el string 'S' - se detecto al probar el flujo real de crear/editar una
bodega despues del cambio de tipo (fallaba con "invalid input syntax for
type boolean: S").

Revision ID: 833750948175
Revises: 3dd4a4c32d50
Create Date: 2026-08-01 15:52:10.447666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '833750948175'
down_revision: Union[str, Sequence[str], None] = '3dd4a4c32d50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.m_bodegas ALTER COLUMN activo TYPE boolean USING (activo = 'S');")
    op.execute("""
        CREATE OR REPLACE FUNCTION public.m_bodegas_validar_limite_plan()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
            DECLARE
                v_id_emp INTEGER;
                v_max_bodegas INTEGER;
                v_actuales INTEGER;
            BEGIN
                IF NOT NEW.activo THEN
                    RETURN NEW;
                END IF;

                SELECT s.id_emp INTO v_id_emp
                FROM public.m_sucursales s
                WHERE s.id = NEW.id_sucursal;

                SELECT p.max_bodegas INTO v_max_bodegas
                FROM public.md_empresas e
                JOIN public.md_planes p ON p.id_plan = e.id_plan
                WHERE e.id_emp = v_id_emp;

                IF v_max_bodegas IS NULL THEN
                    RETURN NEW;
                END IF;

                SELECT count(*) INTO v_actuales
                FROM public.m_bodegas b
                JOIN public.m_sucursales s ON s.id = b.id_sucursal
                WHERE s.id_emp = v_id_emp AND b.activo = true;

                IF v_actuales >= v_max_bodegas THEN
                    RAISE EXCEPTION 'ERR_VAL: Su plan actual permite un maximo de % bodegas activas.', v_max_bodegas;
                END IF;

                RETURN NEW;
            END;
        $function$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_bodegas ALTER COLUMN activo TYPE character varying(2) USING (CASE WHEN activo THEN 'S' ELSE 'N' END);")
    op.execute("""
        CREATE OR REPLACE FUNCTION public.m_bodegas_validar_limite_plan()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
            DECLARE
                v_id_emp INTEGER;
                v_max_bodegas INTEGER;
                v_actuales INTEGER;
            BEGIN
                IF NEW.activo <> 'S' THEN
                    RETURN NEW;
                END IF;

                SELECT s.id_emp INTO v_id_emp
                FROM public.m_sucursales s
                WHERE s.id = NEW.id_sucursal;

                SELECT p.max_bodegas INTO v_max_bodegas
                FROM public.md_empresas e
                JOIN public.md_planes p ON p.id_plan = e.id_plan
                WHERE e.id_emp = v_id_emp;

                IF v_max_bodegas IS NULL THEN
                    RETURN NEW;
                END IF;

                SELECT count(*) INTO v_actuales
                FROM public.m_bodegas b
                JOIN public.m_sucursales s ON s.id = b.id_sucursal
                WHERE s.id_emp = v_id_emp AND b.activo = 'S';

                IF v_actuales >= v_max_bodegas THEN
                    RAISE EXCEPTION 'ERR_VAL: Su plan actual permite un maximo de % bodegas activas.', v_max_bodegas;
                END IF;

                RETURN NEW;
            END;
        $function$;
    """)
