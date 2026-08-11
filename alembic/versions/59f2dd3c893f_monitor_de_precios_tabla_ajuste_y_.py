"""monitor de precios: tabla ajuste y funciones de reporte

Agrega el reporte "Precios" al Monitor de Ventas, mismo patron que el reporte
de Costos en Monitor de Compras: tabla de encabezado para el ajuste manual
(auditable, con observacion obligatoria) + 2 funciones Postgres (kpi/conteo y
listado paginado). A diferencia de costos, el ajuste NO llama a un stored
procedure propio: p_precios ya tiene sus triggers (ins_p_precios/
ins_p_precios_reglas, ver 9c8225580f88) que hacen todo el trabajo con un
INSERT directo, asi que el backend Python inserta en p_precios el mismo tal
cual hace repository_cargastock.py.

Diferencia estructural clave frente a costos: el precio no tiene dimension de
bodega (s_precioxarticulo es por lista, no por bodega), asi que las funciones
de este reporte usan "lista de precios" como filtro/dimension en el lugar
donde costos usa "bodega" - y solo consideran listas base (id_cliente IS
NULL), nunca listas de cliente.

Revision ID: 59f2dd3c893f
Revises: 2d06d117d1da
Create Date: 2026-08-08 20:49:06.097931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59f2dd3c893f'
down_revision: Union[str, Sequence[str], None] = '2d06d117d1da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- t_ajusteprecio_lista: encabezado de ajuste manual, mismo patron que
    # t_ajustecosto_articulo (id_trans comparte la secuencia id_transaccion,
    # nro_docum tiene su propia secuencia dedicada, sin FKs declaradas -
    # mismo criterio ya usado en esa tabla y en p_precios/s_precioxarticulo). ---
    op.execute("CREATE SEQUENCE public.t_ajusteprecio_lista_nro_docum_seq;")

    op.execute("""
        CREATE TABLE public.t_ajusteprecio_lista (
            id_trans BIGINT NOT NULL DEFAULT nextval('id_transaccion'),
            linea INTEGER NOT NULL,
            id_emp INTEGER NOT NULL,
            id_lista INTEGER NOT NULL,
            documento VARCHAR(15) NOT NULL,
            nro_docum INTEGER NOT NULL DEFAULT nextval('t_ajusteprecio_lista_nro_docum_seq'),
            fec_doc DATE NOT NULL,
            id_articulo INTEGER NOT NULL,
            observaciones VARCHAR(250) NULL,
            imp_precio_actual NUMERIC(20,2) NOT NULL,
            imp_precio_nuevo NUMERIC(20,2) NOT NULL,
            vista VARCHAR(16) NOT NULL,
            fecha_mod TIMESTAMP NOT NULL,
            logs JSON NULL,
            PRIMARY KEY (id_trans)
        );
    """)

    # --- Funcion de conteo (para paginacion), mismo shape que
    # monitorcompras_kpi_costos pero uniendo contra s_precioxarticulo/
    # m_listaprecio en vez de s_costoxbodegas/m_bodegas. ---
    op.execute("""
        CREATE OR REPLACE FUNCTION public.monitorventas_kpi_precio(
            param_id_emp integer, param_lista_id integer, param_negocio_id integer,
            param_categoria_id integer, param_subcategoria_id integer,
            param_articulos integer[] DEFAULT NULL::integer[])
        RETURNS TABLE(totalarticulos integer)
        LANGUAGE plpgsql
        AS $function$
            DECLARE
                v_sql TEXT;
            BEGIN
                v_sql := 'select cast(count(A.id_articulo) as integer) totalarticulos from
                            m_articulos A
                            left join (SELECT A.id_lista, A.id_articulo
                                        FROM s_precioxarticulo A
                                        INNER JOIN m_listaprecio C on A.id_lista=C.id_lista
                                        WHERE C.id_cliente IS NULL) B on A.id_articulo=B.id_articulo
                            left join m_negocios G on A.id_negocio=G.id
                            where 1=1 AND G.id_emp = ' || param_id_emp;

                IF param_lista_id <> 0 THEN
                    v_sql := v_sql || ' AND B.id_lista = ' || param_lista_id;
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

    # --- Funcion de listado paginado, mismo shape que monitorcompra_costo. ---
    op.execute("""
        CREATE OR REPLACE FUNCTION public.monitorventas_precio(
            param_id_emp integer, param_lista_id integer, param_negocio_id integer,
            param_categoria_id integer, param_subcategoria_id integer,
            param_limit integer, param_pagina integer,
            param_articulos integer[] DEFAULT NULL::integer[],
            param_incluir_limite boolean DEFAULT true)
        RETURNS TABLE(negocio character varying, idlista integer, lista character varying,
            categoria character varying, subcategoria character varying, idarticulo integer,
            cod_articulo character varying, nom_articulo character varying, precio numeric)
        LANGUAGE plpgsql
        AS $function$
            DECLARE
                v_sql TEXT;
            BEGIN
                v_sql := 'select
                        COALESCE(G.nom_negocio,'''')                  as Negocio,
                        COALESCE(id_lista,0)                          as idlista,
                        COALESCE(NomLista,''Sin Lista'')               as NomLista,
                        COALESCE(E.nom_categoria,'''')                 as categoria,
                        COALESCE(F.nom_subcategoria,'''')              as subCategoria,
                        COALESCE(a.id_articulo,0)                     as idarticulo,
                        a.cod_articulo                                as CodArticulo,
                        a.nom_articulo                                as NomArticulo,
                        COALESCE(B.precio_venta,0)                    as Precio
                        from m_articulos A
                        left join (
                            SELECT A.id_lista, C.nombre as NomLista,
                            A.id_articulo, A.precio_venta
                            FROM s_precioxarticulo A
                            INNER JOIN m_listaprecio C on A.id_lista=C.id_lista
                            WHERE C.id_cliente IS NULL
                        ) B on A.id_articulo=B.id_articulo
                        left join m_categorias E on A.id_categoria=E.id
                        left join m_subcategorias F on A.id_subcategoria=F.id
                        left join m_negocios G on A.id_negocio=G.id
                        where 1=1 AND G.id_emp = ' || param_id_emp;

                IF param_lista_id <> 0 THEN
                    v_sql := v_sql || ' AND B.id_lista = ' || param_lista_id;
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
                    v_sql := v_sql || ' ORDER BY B.NomLista LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
                ELSE
                    v_sql := v_sql || ' ORDER BY B.NomLista';
                END IF;

                RETURN QUERY EXECUTE v_sql USING param_articulos;
            END;
        $function$;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.monitorventas_precio(integer,integer,integer,integer,integer,integer,integer,integer[],boolean);")
    op.execute("DROP FUNCTION IF EXISTS public.monitorventas_kpi_precio(integer,integer,integer,integer,integer,integer[]);")
    op.execute("DROP TABLE IF EXISTS public.t_ajusteprecio_lista;")
    op.execute("DROP SEQUENCE IF EXISTS public.t_ajusteprecio_lista_nro_docum_seq;")
