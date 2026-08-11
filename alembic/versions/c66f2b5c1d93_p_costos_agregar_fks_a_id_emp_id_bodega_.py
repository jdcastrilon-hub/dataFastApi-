"""p_costos: agregar FKs a id_emp, id_bodega, id_articulo

Mismo analisis que se hizo para p_stock (ver
9db63f756e00_p_stock_agregar_fks_a_id_emp_id_bodega_.py y
docs/tecnica/modelos-base-de-datos/p_costos.md): p_costos nacio sin ninguna
FK, pero esa justificacion (referencia polimorfica) solo aplica de verdad a
documento/nro_docum/documento_ref/nro_docum_ref/id_trans_ref (apuntan a una
tabla t_* distinta segun el modulo, o directamente no estan atados a una
sola tabla por diseno). id_emp/id_bodega/id_articulo siempre apuntan a la
misma tabla maestra sin importar que modulo escribio la fila, asi que
agregarles FK no reintroduce el acoplamiento que se queria evitar.

id_proveedor queda fuera a proposito, decision explicita del usuario: usa 0
como valor centinela ("no aplica", ej. Ajuste de Costo) y m_proveedores no
tiene fila con id=0 - mismo caso que id_lote=0 en p_stock, que tambien se
dejo sin FK en vez de materializar una fila centinela.

0 filas huerfanas verificadas para id_emp/id_bodega/id_articulo antes de
agregar las 3 FK (24 filas reales en la tabla al momento de esta migracion,
todas de Compra Directa).

Revision ID: c66f2b5c1d93
Revises: bfe7e402d83f
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c66f2b5c1d93'
down_revision: Union[str, Sequence[str], None] = 'bfe7e402d83f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.p_costos ADD CONSTRAINT p_costos_id_emp_fkey FOREIGN KEY (id_emp) REFERENCES public.md_empresas(id_emp);")
    op.execute("ALTER TABLE public.p_costos ADD CONSTRAINT p_costos_id_bodega_fkey FOREIGN KEY (id_bodega) REFERENCES public.m_bodegas(id);")
    op.execute("ALTER TABLE public.p_costos ADD CONSTRAINT p_costos_id_articulo_fkey FOREIGN KEY (id_articulo) REFERENCES public.m_articulos(id_articulo);")


def downgrade() -> None:
    op.execute("ALTER TABLE public.p_costos DROP CONSTRAINT p_costos_id_articulo_fkey;")
    op.execute("ALTER TABLE public.p_costos DROP CONSTRAINT p_costos_id_bodega_fkey;")
    op.execute("ALTER TABLE public.p_costos DROP CONSTRAINT p_costos_id_emp_fkey;")
