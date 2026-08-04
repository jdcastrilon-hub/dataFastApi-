"""p_stock: agregar FKs a id_emp, id_bodega, id_estado, id_articulo/id_codbarra

p_stock nacio sin ninguna FK (referencia polimorfica completa, ver
base-de-datos.md), pero esa justificacion solo aplica de verdad a
documento/nro_docum (apuntan a una tabla t_* distinta segun el modulo). Las
columnas de dato maestro (id_emp/id_bodega/id_estado/id_articulo/id_codbarra)
siempre apuntan a la misma tabla sin importar que modulo escribio la fila, asi
que agregarles FK no reintroduce el acoplamiento que se queria evitar.

id_articulo/id_codbarra van como FK COMPUESTA hacia m_artxcodigobarra
(id_articulo, id_codbarra) - esa es su PK real, id_codbarra solo no tiene
constraint unique propio (aunque en la practica si es unico, generado por
secuencia).

Se encontro y limpio 1 fila huerfana real antes de agregar la FK: p_stock de
un CargaStock de prueba (id_trans=349) apuntando a id_codbarra=6022, que ya
no existia en m_artxcodigobarra (el codigo de barra de ese articulo se habia
recreado con un id nuevo, 6027, en vez de editarse in-place). Se reasigno esa
fila al id_codbarra vigente del mismo articulo.

id_lote queda fuera a proposito por ahora: usa 0 como valor centinela ("no
maneja lote"), y m_lotes no tiene fila con id=0 - haria falta decidir si se
materializa esa fila o se migra el centinela a NULL antes de poder agregar
la FK.

Revision ID: 9db63f756e00
Revises: 6084470835cb
Create Date: 2026-07-31 10:34:50.508396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9db63f756e00'
down_revision: Union[str, Sequence[str], None] = '6084470835cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.p_stock ADD CONSTRAINT p_stock_id_emp_fkey FOREIGN KEY (id_emp) REFERENCES public.md_empresas(id_emp);")
    op.execute("ALTER TABLE public.p_stock ADD CONSTRAINT p_stock_id_bodega_fkey FOREIGN KEY (id_bodega) REFERENCES public.m_bodegas(id);")
    op.execute("ALTER TABLE public.p_stock ADD CONSTRAINT p_stock_id_estado_fkey FOREIGN KEY (id_estado) REFERENCES public.m_estados(id);")
    op.execute("ALTER TABLE public.p_stock ADD CONSTRAINT p_stock_id_articulo_fkey FOREIGN KEY (id_articulo) REFERENCES public.m_articulos(id_articulo);")

    # Huerfano puntual (ver nota arriba) - reasignar antes de que la FK compuesta lo bloquee.
    op.execute("UPDATE public.p_stock SET id_codbarra=6027 WHERE id_trans=349 AND id_codbarra=6022;")
    op.execute("ALTER TABLE public.p_stock ADD CONSTRAINT p_stock_id_articulo_codbarra_fkey FOREIGN KEY (id_articulo, id_codbarra) REFERENCES public.m_artxcodigobarra(id_articulo, id_codbarra);")


def downgrade() -> None:
    op.execute("ALTER TABLE public.p_stock DROP CONSTRAINT p_stock_id_articulo_codbarra_fkey;")
    op.execute("ALTER TABLE public.p_stock DROP CONSTRAINT p_stock_id_articulo_fkey;")
    op.execute("ALTER TABLE public.p_stock DROP CONSTRAINT p_stock_id_estado_fkey;")
    op.execute("ALTER TABLE public.p_stock DROP CONSTRAINT p_stock_id_bodega_fkey;")
    op.execute("ALTER TABLE public.p_stock DROP CONSTRAINT p_stock_id_emp_fkey;")
