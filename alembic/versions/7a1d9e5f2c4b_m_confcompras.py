"""m_confcompras (configuracion de compras por empresa)

Revision ID: 7a1d9e5f2c4b
Revises: 8e3f23494133
Create Date: 2026-09-13 00:00:00.000000

m_confcompras: 1 fila por empresa, configuracion del modulo Compras. Mismo
patron que m_confcomercial (Comercial): singleton por id_emp, sin logica
propia mas alla de leer/guardar - la usan otros modulos para resolver
valores por defecto en vez de dejarlos elegir al usuario.

- id_estado_comp: estado de mercancia (m_estados) que se asigna por defecto
  a toda Compra Directa. Hoy el usuario elige el estado en el formulario
  (combo-estadostock -> t_compras.id_estado); deja de ser seleccionable y
  pasa a ser un valor fijo por empresa. Se guarda como entero con FK real a
  m_estados.id (mismo tipo que t_compras.id_estado, que tampoco tiene FK
  propia hoy - no se corrige ese gap aca, es aparte) en vez del texto
  cod_estado, para no tener que resolver el id en cada compra.
- act_precio_compra: si la empresa quiere digitar precio de venta/utilidad
  directamente en la Compra Directa (futuro) o si ese proceso lo maneja
  aparte, por la lista de precios (Carga de Precios / ajuste manual). Deny
  by default (false) - hasta no configurarlo, Compra Directa no muestra esos
  campos cuando se agreguen.

Sin logs/roles asociados por ahora (a diferencia de m_confcomercial, que
trae ademas la grilla m_confcomercial_dctoxrol) - se agrega si compras
termina necesitando un desglose similar.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7a1d9e5f2c4b'
down_revision = '8e3f23494133'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.m_confcompras (
            id_emp              integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_estado_comp      integer NULL REFERENCES public.m_estados(id),
            act_precio_compra   boolean NOT NULL DEFAULT false,
            fecha_mod           timestamp NOT NULL DEFAULT now(),
            logs                json NULL,
            PRIMARY KEY (id_emp)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.m_confcompras")
