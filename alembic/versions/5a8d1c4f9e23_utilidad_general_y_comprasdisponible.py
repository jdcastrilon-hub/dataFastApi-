"""m_confcompras.porc_utilidad_general + comprasdisponiblexbodega resuelve utilidad

Revision ID: 5a8d1c4f9e23
Revises: 3e7b8f6c2a91
Create Date: 2026-09-13 00:00:00.000000

- m_confcompras.porc_utilidad_general: ultimo nivel de la jerarquia de
  utilidad (subcategoria -> categoria -> general). Nullable: si la empresa
  no configuro nada en ningun nivel, no hay sugerencia (NULL, no 0 - 0%
  markup es una configuracion valida en si misma, distinta de "nada
  configurado").
- comprasdisponiblexbodega: ya hace JOIN a m_articulos para resolver el
  impuesto (usa el mismo param_articulo_id que ya recibe) - se aprovecha esa
  misma consulta para traer id_emp/id_categoria/id_subcategoria y resolver la
  jerarquia completa ahi mismo, sin agregar parametros nuevos a la funcion ni
  tocar la firma del endpoint /core/services/ini/compraDisponiblexBodega.
  Nueva columna de salida: porc_utilidad (NULL si no hay nada configurado en
  ningun nivel).
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '5a8d1c4f9e23'
down_revision = '3e7b8f6c2a91'
branch_labels = None
depends_on = None


FUNCION_ANTERIOR = """
CREATE OR REPLACE FUNCTION public.comprasdisponiblexbodega(param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer, param_estado_id integer, param_id_proveedor integer)
 RETURNS TABLE(stock integer, costo numeric, impuesto integer, porcentaje numeric)
 LANGUAGE plpgsql
AS $function$

DECLARE
	v_stock integer;
	v_costo numeric(20,2);
	v_impuesto integer;
	v_porcentaje numeric;
BEGIN

	select cantidad from s_stkbodegas INTO v_stock
	where id_bodega=param_bodega_id
	and id_estado=param_estado_id
	and id_articulo=param_articulo_id
	and id_codbarra=param_id_codbarra;

	select imp_costo_unitario  from s_costoxbodegas  INTO v_costo
	where id_bodega=param_bodega_id
	and id_articulo=param_articulo_id;

	select id_impuesto,B.porc_tasa from m_articulos A
	inner join m_impuesto B on A.id_impuesto=B.id
	INTO v_impuesto,v_porcentaje
	where id_articulo=param_articulo_id;

	RETURN QUERY
	SELECT
		COALESCE(v_stock, 0),
		COALESCE(v_costo, 0),
		COALESCE(v_impuesto, 0),
		COALESCE(v_porcentaje, 0);
END
$function$
"""

FUNCION_NUEVA = """
CREATE OR REPLACE FUNCTION public.comprasdisponiblexbodega(param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer, param_estado_id integer, param_id_proveedor integer)
 RETURNS TABLE(stock integer, costo numeric, impuesto integer, porcentaje numeric, porc_utilidad numeric)
 LANGUAGE plpgsql
AS $function$

DECLARE
	v_stock integer;
	v_costo numeric(20,2);
	v_impuesto integer;
	v_porcentaje numeric;
	v_id_emp integer;
	v_id_categoria integer;
	v_id_subcategoria integer;
	v_porc_utilidad numeric;
BEGIN

	select cantidad from s_stkbodegas INTO v_stock
	where id_bodega=param_bodega_id
	and id_estado=param_estado_id
	and id_articulo=param_articulo_id
	and id_codbarra=param_id_codbarra;

	select imp_costo_unitario  from s_costoxbodegas  INTO v_costo
	where id_bodega=param_bodega_id
	and id_articulo=param_articulo_id;

	select A.id_impuesto, B.porc_tasa, A.id_emp, A.id_categoria, A.id_subcategoria
	from m_articulos A
	inner join m_impuesto B on A.id_impuesto=B.id
	INTO v_impuesto, v_porcentaje, v_id_emp, v_id_categoria, v_id_subcategoria
	where A.id_articulo=param_articulo_id;

	-- Jerarquia de utilidad (markup sugerido): subcategoria -> categoria -> general.
	-- Se corta en el primer nivel que tenga una fila activa; si ninguno tiene,
	-- v_porc_utilidad queda NULL (no se sugiere nada, no es "0%").
	-- Columnas calificadas con alias de tabla: "porc_utilidad" a secas es
	-- ambiguo entre esta columna de m_categoriasxutilidad y la columna de
	-- salida homonima de la funcion (RETURNS TABLE) - error real encontrado
	-- al probar en vivo (AmbiguousColumn).
	if v_id_subcategoria is not null then
		select U.porc_utilidad into v_porc_utilidad
		from m_categoriasxutilidad U
		where U.id_emp=v_id_emp and U.id_categoria=v_id_categoria
		  and U.id_subcategoria=v_id_subcategoria and U.activo=true;
	end if;

	if v_porc_utilidad is null then
		select U.porc_utilidad into v_porc_utilidad
		from m_categoriasxutilidad U
		where U.id_emp=v_id_emp and U.id_categoria=v_id_categoria
		  and U.id_subcategoria is null and U.activo=true;
	end if;

	if v_porc_utilidad is null then
		select C.porc_utilidad_general into v_porc_utilidad
		from m_confcompras C
		where C.id_emp=v_id_emp;
	end if;

	RETURN QUERY
	SELECT
		COALESCE(v_stock, 0),
		COALESCE(v_costo, 0),
		COALESCE(v_impuesto, 0),
		COALESCE(v_porcentaje, 0),
		v_porc_utilidad;
END
$function$
"""


FIRMA_FUNCION = "comprasdisponiblexbodega(integer, integer, integer, integer, integer)"


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.m_confcompras
        ADD COLUMN porc_utilidad_general numeric(5,2) NULL;
    """)

    # Postgres no permite CREATE OR REPLACE FUNCTION cuando cambia el tipo de
    # retorno (agregar una columna a un RETURNS TABLE cuenta como cambio) -
    # hay que borrarla primero, igual que con el overload de sp_compradirecta
    # en la migracion 9f2c6a1e4d78.
    op.execute(f"DROP FUNCTION IF EXISTS public.{FIRMA_FUNCION}")
    op.execute(FUNCION_NUEVA)


def downgrade() -> None:
    op.execute(f"DROP FUNCTION IF EXISTS public.{FIRMA_FUNCION}")
    op.execute(FUNCION_ANTERIOR)
    op.execute("ALTER TABLE public.m_confcompras DROP COLUMN IF EXISTS porc_utilidad_general")
