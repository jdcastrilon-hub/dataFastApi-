"""m_personas: agregar id_emp (cada empresa maneja su propio directorio de personas)

Hallazgo real durante el diseno del modal "Seleccionar persona" (Proveedores/
Clientes): m_personas no tenia id_emp - un buscador de personas (combo-persona,
find_persona_by_query) sin filtrar por empresa significa que cualquier empresa
del sistema puede encontrar y reutilizar (y potencialmente corregir, ya que el
formulario permite editar los datos de la persona ligada) una persona creada
originalmente por OTRA empresa. Decision del usuario: cada empresa debe manejar
su propio directorio de personas, independiente - se agrega id_emp, poblado con
la empresa que la creo (desde Proveedor, Cliente o Usuario, el unico dato
disponible retroactivamente).

Backfill:
1. Limpieza previa: se eliminan 4 personas huerfanas (sin proveedor/cliente/
   usuario que las referencie) creadas como datos de prueba desechables durante
   la verificacion de responsable_iva/observacion en esta misma sesion.
2. id_emp se toma de whichever de m_proveedores/m_clientes/md_usuarios referencia
   primero a esa persona (prioridad en ese orden; desempate por id_emp para que
   sea deterministico). Real, no hipotetico: la persona id=27 ("Inventario
   Inicial - Sin Proveedor") esta referenciada HOY por proveedores de dos
   empresas distintas (id_emp=1 y id_emp=8) - artefacto historico del diseno sin
   id_emp, no se puede resolver "correctamente" en retrospectiva, se resuelve
   determinista (queda con la empresa de menor id_emp) y se documenta aqui.
3. Personas sin ningun proveedor/cliente/usuario que las referencie (datos de
   prueba huerfanos, ya desconectados de cualquier registro vivo) quedan en
   id_emp=1 por defecto - no hay ninguna evidencia de a que empresa pertenecian.

cod_tit pasa de UNIQUE global a UNIQUE(id_emp, cod_tit) - mismo tratamiento que
ya se aplico a m_estados/m_motivoajuste/m_motivodevolucion/m_impuesto: con
personas ahora scoped por empresa, dos empresas distintas SI pueden registrar
la misma cedula/NIT como personas independientes.

Revision ID: 8e3f23494133
Revises: c8255c74d8be
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3f23494133'
down_revision: Union[str, Sequence[str], None] = 'c8255c74d8be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Limpieza de personas de prueba huerfanas dejadas por esta sesion
    op.execute("DELETE FROM public.m_personas WHERE id_persona IN (42, 43, 44, 45);")

    # 2. Columna nullable primero, para poder rellenarla
    op.execute("ALTER TABLE public.m_personas ADD COLUMN id_emp INTEGER;")

    # 3. Backfill desde quien la referencia (proveedor > cliente > usuario)
    op.execute("""
        UPDATE public.m_personas p SET id_emp = sub.id_emp FROM (
            SELECT DISTINCT ON (id_persona) id_persona, id_emp
            FROM (
                SELECT id_persona, id_emp, 1 AS prioridad FROM public.m_proveedores
                UNION ALL
                SELECT id_persona, id_emp, 2 AS prioridad FROM public.m_clientes
                UNION ALL
                SELECT id_persona, id_emp_principal AS id_emp, 3 AS prioridad FROM public.md_usuarios
            ) fuentes
            ORDER BY id_persona, prioridad, id_emp
        ) sub
        WHERE p.id_persona = sub.id_persona;
    """)

    # 4. Huerfanas sin ninguna referencia viva: sin evidencia de empresa, quedan en la 1
    op.execute("UPDATE public.m_personas SET id_emp = 1 WHERE id_emp IS NULL;")

    op.execute("ALTER TABLE public.m_personas ALTER COLUMN id_emp SET NOT NULL;")
    op.execute("ALTER TABLE public.m_personas ADD CONSTRAINT fk_m_personas_empresa FOREIGN KEY (id_emp) REFERENCES public.md_empresas(id_emp);")

    # 5. cod_tit: de unico global a unico por empresa
    op.execute("ALTER TABLE public.m_personas DROP CONSTRAINT m_personas_uniq;")
    op.execute("ALTER TABLE public.m_personas ADD CONSTRAINT m_personas_uniq UNIQUE (id_emp, cod_tit);")


def downgrade() -> None:
    op.execute("ALTER TABLE public.m_personas DROP CONSTRAINT m_personas_uniq;")
    op.execute("ALTER TABLE public.m_personas ADD CONSTRAINT m_personas_uniq UNIQUE (cod_tit);")

    op.execute("ALTER TABLE public.m_personas DROP CONSTRAINT fk_m_personas_empresa;")
    op.execute("ALTER TABLE public.m_personas DROP COLUMN id_emp;")
    # Las 4 personas de prueba eliminadas en upgrade() no se restauran.
