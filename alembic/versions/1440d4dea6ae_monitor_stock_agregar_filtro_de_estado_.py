"""monitor stock: agregar filtro de estado a monitorstock_kpi y monitorstock_vista1

Se agrego un parametro param_estado_id (DEFAULT 0, sin filtro) a ambas
funciones para el nuevo select de "Estado" en el Monitor de Stock (vista
inventario), con la misma logica que ya usan bodega/negocio/categoria
(IF param_x <> 0 THEN agrega el AND).

Nota tecnica (para no repetir el error): la primera vez que se hizo este
cambio se uso CREATE OR REPLACE agregando el parametro nuevo al final -
Postgres identifica una funcion por (nombre + tipos de argumento), asi que
agregar un parametro cambia la firma y CREATE OR REPLACE termina creando una
SOBRECARGA nueva en vez de reemplazar la funcion vieja, dejando 2 versiones
coexistiendo (la vieja, sin estado, seguia ahi sin que nada la usara mas).
Se detecto y limpio manualmente (DROP FUNCTION de la firma vieja) antes de
esta migracion. Esta migracion ya aplica el cambio correctamente: DROP de la
firma anterior seguido de CREATE, no CREATE OR REPLACE con una firma distinta.

Revision ID: 1440d4dea6ae
Revises: 9db63f756e00
Create Date: 2026-07-31 21:03:10.914802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1440d4dea6ae'
down_revision: Union[str, Sequence[str], None] = '9db63f756e00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.monitorstock_kpi(integer, integer, integer, integer, integer, integer[]);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[], param_estado_id integer DEFAULT 0)
         RETURNS TABLE(totalarticulos integer)
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_sql TEXT;
        BEGIN
            v_sql := 'select cast(count(*) as integer) totalarticulos from m_articulos A
                    left join m_artxcodigobarra CB on A.id_articulo = CB.id_articulo
                    left join (SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                    A.id_articulo,A.id_codbarra,A.id_estado,A.cantidad
                    FROM s_stkbodegas A
                    INNER JOIN m_bodegas B on A.id_bodega=B.id) B on CB.id_articulo=B.id_articulo AND CB.id_codbarra=B.id_codbarra
                    left join m_negocios G on A.id_negocio=G.id
                    where 1=1 AND G.id_emp = ' || param_id_emp;

            IF param_bodega_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_bodega = ' || param_bodega_id;
            END IF;

            IF param_negocio_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_negocio = ' || param_negocio_id;
            END IF;

            IF param_categoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_categoria = ' || param_categoria_id;
            END IF;

            IF param_subcategoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_subcategoria = ' || param_subcategoria_id;
            END IF;

            IF param_estado_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_estado = ' || param_estado_id;
            END IF;

            v_sql := v_sql || ' AND ($1 IS NULL OR array_length($1,1) IS NULL OR A.id_articulo = ANY($1))';

            RETURN QUERY EXECUTE v_sql USING param_articulos;
        END;
        $function$;
    """)

    op.execute("DROP FUNCTION IF EXISTS public.monitorstock_vista1(integer, integer, integer, integer, integer, integer, integer, integer[], boolean);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true, param_estado_id integer DEFAULT 0)
         RETURNS TABLE(negocio character varying, bodega character varying, categoria character varying, subcategoria character varying, id_articulo integer, cod_articulo character varying, nom_articulo character varying, id_codbarra integer, cod_barra character varying, estado character varying, unidad character varying, cantidad integer)
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_sql TEXT;
        BEGIN
            v_sql := 'select
                    COALESCE(G.nom_negocio,'''')					as Negocio,
                    COALESCE(CodigoBodega,''Sin Bodega'')			as NomBodega,
                    COALESCE(E.nom_categoria,'''')					as categoria,
                    COALESCE(F.nom_subcategoria,'''')					as subCategoria,
                    a.id_articulo									as IdArticulo,
                    a.cod_articulo                  				as CodArticulo,
                    a.nom_articulo                 			    	as NomArticulo,
                    CB.id_codbarra									as IdCodBarra,
                    COALESCE(CB.cod_barra,'''')						as CodBarra,
                    COALESCE(c.cod_estado,'''')						as Estado,
                    D.cod_unidad									as Unidad,
                    COALESCE(B.cantidad,0)         					as Cantidad
                    from m_articulos A
                    left join m_artxcodigobarra CB on A.id_articulo = CB.id_articulo
                    left join (
                        SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                        A.id_articulo,A.id_codbarra,A.id_estado,A.cantidad
                        FROM s_stkbodegas A
                        INNER JOIN m_bodegas B on A.id_bodega=B.id) B on CB.id_articulo=B.id_articulo AND CB.id_codbarra=B.id_codbarra
                    left join m_estados C on B.id_estado=C.id
                    left join m_unidades D on A.id_unidad=D.id
                    left join m_categorias E on A.id_categoria=E.id
                    left join m_subcategorias F on A.id_subcategoria=F.id
                    left join m_negocios G on A.id_negocio=G.id
                    where 1=1 AND G.id_emp = ' || param_id_emp;

            IF param_bodega_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_bodega = ' || param_bodega_id;
            END IF;

            IF param_negocio_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_negocio = ' || param_negocio_id;
            END IF;

            IF param_categoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_categoria = ' || param_categoria_id;
            END IF;

            IF param_subcategoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_subcategoria = ' || param_subcategoria_id;
            END IF;

            IF param_estado_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_estado = ' || param_estado_id;
            END IF;

            v_sql := v_sql || ' AND ($1 IS NULL OR array_length($1,1) IS NULL OR A.id_articulo = ANY($1))';

            IF param_incluir_limite THEN
                v_sql := v_sql || ' ORDER BY B.CodigoBodega LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
            ELSE
                v_sql := v_sql || ' ORDER BY B.CodigoBodega';
            END IF;

            RETURN QUERY EXECUTE v_sql USING param_articulos;
        END;
        $function$;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.monitorstock_vista1(integer, integer, integer, integer, integer, integer, integer, integer[], boolean, integer);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
         RETURNS TABLE(negocio character varying, bodega character varying, categoria character varying, subcategoria character varying, id_articulo integer, cod_articulo character varying, nom_articulo character varying, id_codbarra integer, cod_barra character varying, estado character varying, unidad character varying, cantidad integer)
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_sql TEXT;
        BEGIN
            v_sql := 'select
                    COALESCE(G.nom_negocio,'''')					as Negocio,
                    COALESCE(CodigoBodega,''Sin Bodega'')			as NomBodega,
                    COALESCE(E.nom_categoria,'''')					as categoria,
                    COALESCE(F.nom_subcategoria,'''')					as subCategoria,
                    a.id_articulo									as IdArticulo,
                    a.cod_articulo                  				as CodArticulo,
                    a.nom_articulo                 			    	as NomArticulo,
                    CB.id_codbarra									as IdCodBarra,
                    COALESCE(CB.cod_barra,'''')						as CodBarra,
                    COALESCE(c.cod_estado,'''')						as Estado,
                    D.cod_unidad									as Unidad,
                    COALESCE(B.cantidad,0)         					as Cantidad
                    from m_articulos A
                    left join m_artxcodigobarra CB on A.id_articulo = CB.id_articulo
                    left join (
                        SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                        A.id_articulo,A.id_codbarra,A.id_estado,A.cantidad
                        FROM s_stkbodegas A
                        INNER JOIN m_bodegas B on A.id_bodega=B.id) B on CB.id_articulo=B.id_articulo AND CB.id_codbarra=B.id_codbarra
                    left join m_estados C on B.id_estado=C.id
                    left join m_unidades D on A.id_unidad=D.id
                    left join m_categorias E on A.id_categoria=E.id
                    left join m_subcategorias F on A.id_subcategoria=F.id
                    left join m_negocios G on A.id_negocio=G.id
                    where 1=1 AND G.id_emp = ' || param_id_emp;

            IF param_bodega_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_bodega = ' || param_bodega_id;
            END IF;

            IF param_negocio_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_negocio = ' || param_negocio_id;
            END IF;

            IF param_categoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_categoria = ' || param_categoria_id;
            END IF;

            IF param_subcategoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_subcategoria = ' || param_subcategoria_id;
            END IF;

            v_sql := v_sql || ' AND ($1 IS NULL OR array_length($1,1) IS NULL OR A.id_articulo = ANY($1))';

            IF param_incluir_limite THEN
                v_sql := v_sql || ' ORDER BY B.CodigoBodega LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
            ELSE
                v_sql := v_sql || ' ORDER BY B.CodigoBodega';
            END IF;

            RETURN QUERY EXECUTE v_sql USING param_articulos;
        END;
        $function$;
    """)

    op.execute("DROP FUNCTION IF EXISTS public.monitorstock_kpi(integer, integer, integer, integer, integer, integer[], integer);")
    op.execute("""
        CREATE FUNCTION public.monitorstock_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
         RETURNS TABLE(totalarticulos integer)
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_sql TEXT;
        BEGIN
            v_sql := 'select cast(count(*) as integer) totalarticulos from m_articulos A
                    left join m_artxcodigobarra CB on A.id_articulo = CB.id_articulo
                    left join (SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                    A.id_articulo,A.id_codbarra,A.id_estado,A.cantidad
                    FROM s_stkbodegas A
                    INNER JOIN m_bodegas B on A.id_bodega=B.id) B on CB.id_articulo=B.id_articulo AND CB.id_codbarra=B.id_codbarra
                    left join m_negocios G on A.id_negocio=G.id
                    where 1=1 AND G.id_emp = ' || param_id_emp;

            IF param_bodega_id <> 0 THEN
                v_sql := v_sql || ' AND B.id_bodega = ' || param_bodega_id;
            END IF;

            IF param_negocio_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_negocio = ' || param_negocio_id;
            END IF;

            IF param_categoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_categoria = ' || param_categoria_id;
            END IF;

            IF param_subcategoria_id <> 0 THEN
                v_sql := v_sql || ' AND A.id_subcategoria = ' || param_subcategoria_id;
            END IF;

            v_sql := v_sql || ' AND ($1 IS NULL OR array_length($1,1) IS NULL OR A.id_articulo = ANY($1))';

            RETURN QUERY EXECUTE v_sql USING param_articulos;
        END;
        $function$;
    """)
