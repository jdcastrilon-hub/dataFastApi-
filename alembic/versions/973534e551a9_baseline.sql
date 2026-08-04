-- SECUENCIAS
CREATE SEQUENCE IF NOT EXISTS public."contado_1";
CREATE SEQUENCE IF NOT EXISTS public."id_nrodocum_ajustestock";
CREATE SEQUENCE IF NOT EXISTS public."id_nrodocum_compra";
CREATE SEQUENCE IF NOT EXISTS public."id_nrodocum_trasladobodega";
CREATE SEQUENCE IF NOT EXISTS public."id_transaccion";
CREATE SEQUENCE IF NOT EXISTS public."m_articulos_id_articulo_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_artxcodigobarra_id_codbarra_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_bodegas_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_cajas_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_cajasxuser_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_categorias_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_ciudades_id_ciudad_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_clientes_id_cliente_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_conceptoscaja_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_conceptoscajaxuser_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_costeo_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_departamentos_id_departamento_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_empresa_id_emp_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_estados_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_impuesto_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_lotes_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_mediopagos_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_motivoajuste_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_motivodevolucion_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_negocios_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_pais_id_pais_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_personas_id_persona_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_proveedores_id_proveedor_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_subcategorias_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_sucursales_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_tipodocumentos_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_tipoimpuesto_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_tiposervicio_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_ubicaciones_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."m_unidades_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_menu_id_menu_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_menu_permisos_id_menu_permiso_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_modulo_id_modulo_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_permiso_id_permiso_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_permisos_id_permiso_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_rol_id_rol_seq";
CREATE SEQUENCE IF NOT EXISTS public."md_usuarios_id_usuario_seq";
CREATE SEQUENCE IF NOT EXISTS public."t_abrirturno_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."t_ajustecosto_articulo_nro_docum_seq";
CREATE SEQUENCE IF NOT EXISTS public."t_movcajas_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."td_abrirturno_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."td_cierreturno_id_seq";
CREATE SEQUENCE IF NOT EXISTS public."td_facturas_mediopago_id_seq";

-- TABLAS
CREATE TABLE public.m_cajas (
	id INTEGER DEFAULT nextval('m_cajas_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_sucursal_emp INTEGER NOT NULL, 
	cod_caja VARCHAR(15) NOT NULL, 
	nom_caja VARCHAR(100) NOT NULL, 
	cajapos BOOLEAN NOT NULL, 
	status BOOLEAN NOT NULL, 
	id_cliente INTEGER, 
	id_bodega INTEGER, 
	id_estado INTEGER, 
	documento VARCHAR(10), 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	horas_turno INTEGER, 
	CONSTRAINT m_cajas_pkey PRIMARY KEY (id), 
	CONSTRAINT m_cajas_unique UNIQUE NULLS DISTINCT (id_emp, id_sucursal_emp, cod_caja)
);

CREATE TABLE public.m_categorias (
	id INTEGER DEFAULT nextval('m_categorias_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_categoria VARCHAR(15) NOT NULL, 
	nom_categoria VARCHAR(50), 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	estado BOOLEAN, 
	CONSTRAINT m_categorias_pkey PRIMARY KEY (id), 
	CONSTRAINT m_categorias_cod_emp_cod_categoria_key UNIQUE NULLS DISTINCT (id_emp, cod_categoria)
);

CREATE TABLE public.m_costeo (
	id INTEGER DEFAULT nextval('m_costeo_id_seq'::regclass) NOT NULL, 
	tipo_costeo VARCHAR(20) NOT NULL, 
	nombre_costeo VARCHAR(50) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_costeo_pk PRIMARY KEY (id)
);

CREATE TABLE public.m_documventas (
	id_emp INTEGER NOT NULL, 
	id_sucursal_emp INTEGER NOT NULL, 
	documento VARCHAR(16) NOT NULL, 
	descripcion VARCHAR(50) NOT NULL, 
	serie_docum VARCHAR(8) NOT NULL, 
	clase_docum VARCHAR(50) NOT NULL, 
	secuencia VARCHAR(50) NOT NULL, 
	aplica_pos VARCHAR(2) NOT NULL, 
	activo VARCHAR(2) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT m_documventas_pk PRIMARY KEY (id_emp, id_sucursal_emp, documento)
);

CREATE TABLE public.m_documventasxuser (
	id_emp INTEGER NOT NULL, 
	id_sucursal_emp INTEGER NOT NULL, 
	documento VARCHAR(16) NOT NULL, 
	usuario VARCHAR(16) NOT NULL, 
	descripcion VARCHAR(50) NOT NULL, 
	CONSTRAINT m_documventasxuser_pk PRIMARY KEY (id_emp, id_sucursal_emp, documento, usuario)
);

CREATE TABLE public.m_estados (
	id INTEGER DEFAULT nextval('m_estados_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_estado VARCHAR(20) NOT NULL, 
	nom_estado VARCHAR(80) NOT NULL, 
	activo BOOLEAN NOT NULL, 
	obervacion VARCHAR(250) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_estados_pk PRIMARY KEY (id), 
	CONSTRAINT m_estados_unique UNIQUE NULLS DISTINCT (cod_estado)
);

CREATE TABLE public.m_mediopagos (
	id INTEGER DEFAULT nextval('m_mediopagos_id_seq'::regclass) NOT NULL, 
	tipo VARCHAR(20), 
	orden INTEGER, 
	id_emp INTEGER NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	logs JSON, 
	CONSTRAINT m_mediopagos_pkey PRIMARY KEY (id), 
	CONSTRAINT m_mediopagos_unique UNIQUE NULLS DISTINCT (id_emp, tipo)
);

CREATE TABLE public.m_pais (
	id_pais INTEGER DEFAULT nextval('m_pais_id_pais_seq'::regclass) NOT NULL, 
	cod_pais VARCHAR(10) NOT NULL, 
	nom_pais VARCHAR(50) NOT NULL, 
	CONSTRAINT m_pais_pk PRIMARY KEY (id_pais)
);

CREATE TABLE public.m_tipodocumentos (
	id INTEGER DEFAULT nextval('m_tipodocumentos_id_seq'::regclass) NOT NULL, 
	cod_tipodoc VARCHAR(5) NOT NULL, 
	nom_tipodoc VARCHAR(50) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT m_tipodocumentos_pk PRIMARY KEY (id)
);

CREATE TABLE public.m_tipoimpuesto (
	id INTEGER DEFAULT nextval('m_tipoimpuesto_id_seq'::regclass) NOT NULL, 
	tipoimpu VARCHAR(10) NOT NULL, 
	nombre_impuesto VARCHAR(50) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT m_tipoimpuesto_pk PRIMARY KEY (id), 
	CONSTRAINT m_tipoimpuesto_pk_unic UNIQUE NULLS DISTINCT (tipoimpu)
);

CREATE TABLE public.md_empresas (
	id_emp INTEGER DEFAULT nextval('m_empresa_id_emp_seq'::regclass) NOT NULL, 
	nom_emp VARCHAR(50) NOT NULL, 
	razon_social VARCHAR(50) NOT NULL, 
	cod_doc VARCHAR(5) NOT NULL, 
	nit VARCHAR(20) NOT NULL, 
	direccion VARCHAR(50) NOT NULL, 
	cod_ciudad INTEGER NOT NULL, 
	telefono VARCHAR(15) NOT NULL, 
	correo VARCHAR(50) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	id_shard INTEGER DEFAULT 1 NOT NULL, 
	CONSTRAINT m_empresa_pk PRIMARY KEY (id_emp)
);

CREATE TABLE public.md_modulo (
	id_modulo INTEGER DEFAULT nextval('md_modulo_id_modulo_seq'::regclass) NOT NULL, 
	codigo VARCHAR(30) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion VARCHAR(250), 
	icono VARCHAR(100), 
	orden INTEGER DEFAULT 0 NOT NULL, 
	activo BOOLEAN DEFAULT true NOT NULL, 
	CONSTRAINT md_modulo_pkey PRIMARY KEY (id_modulo), 
	CONSTRAINT md_modulo_codigo_key UNIQUE NULLS DISTINCT (codigo)
);

CREATE TABLE public.md_permiso (
	id_permiso INTEGER DEFAULT nextval('md_permiso_id_permiso_seq'::regclass) NOT NULL, 
	codigo VARCHAR(80) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion VARCHAR(250), 
	activo BOOLEAN DEFAULT true NOT NULL, 
	CONSTRAINT md_permiso_pkey PRIMARY KEY (id_permiso), 
	CONSTRAINT md_permiso_codigo_key UNIQUE NULLS DISTINCT (codigo)
);

CREATE TABLE public.md_permisos (
	id_permiso INTEGER DEFAULT nextval('md_permisos_id_permiso_seq'::regclass) NOT NULL, 
	codigo VARCHAR(20) NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	CONSTRAINT md_permisos_pkey PRIMARY KEY (id_permiso), 
	CONSTRAINT md_permisos_codigo_key UNIQUE NULLS DISTINCT (codigo)
);

CREATE TABLE public.p_costos (
	id_trans INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	id_trans_ref INTEGER NOT NULL, 
	documento VARCHAR(15) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	documento_ref VARCHAR(15), 
	nro_docum_ref INTEGER, 
	id_proveedor INTEGER NOT NULL, 
	fec_doc DATE NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	signo INTEGER NOT NULL, 
	imp_costo_actual NUMERIC(20, 2) NOT NULL, 
	imp_costo_nuevo NUMERIC(20, 2) NOT NULL, 
	imp_costo_adicional NUMERIC(20, 2), 
	stock_actual INTEGER NOT NULL, 
	stock_nuevo INTEGER NOT NULL, 
	imp_costo_total NUMERIC(20, 2) NOT NULL, 
	imp_costo_unitario NUMERIC(20, 2) NOT NULL, 
	vista VARCHAR(20) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT p_costos_pkey PRIMARY KEY (id_trans, id_articulo, linea)
);

CREATE TABLE public.p_stock (
	id_trans INTEGER NOT NULL, 
	id_emp INTEGER NOT NULL, 
	documento VARCHAR(15) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	documento_ref VARCHAR(15), 
	nro_ref INTEGER, 
	fec_doc DATE NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	id_ubicacion INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	signo INTEGER NOT NULL, 
	fec_venc DATE, 
	vista VARCHAR(20) NOT NULL, 
	linea INTEGER NOT NULL, 
	serie VARCHAR(10) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT p_stock_pk PRIMARY KEY (id_trans, vista, linea, serie)
);

CREATE TABLE public.s_costoxbodegas (
	id_bodega INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	imp_costo_unitario NUMERIC(20, 2) NOT NULL, 
	proceso VARCHAR(20) NOT NULL, 
	CONSTRAINT s_costoxbodegas_pk PRIMARY KEY (id_bodega, id_articulo)
);

CREATE TABLE public.s_stkbodegas (
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	proceso VARCHAR(20) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT s_stkbodegas_pk PRIMARY KEY (id_bodega, id_estado, id_articulo, id_codbarra)
);

CREATE TABLE public.s_stkbodegaxlote (
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	proceso VARCHAR(20) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT s_stkbodegaxlote_pk PRIMARY KEY (id_bodega, id_estado, id_articulo, id_lote)
);

CREATE TABLE public.s_stkestados (
	id_estado INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	proceso VARCHAR(20) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT s_stkestados_pk PRIMARY KEY (id_estado, id_articulo, id_codbarra)
);

CREATE TABLE public.t_ajustecosto_articulo (
	id_trans INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	documento VARCHAR(15) NOT NULL, 
	nro_docum INTEGER DEFAULT nextval('t_ajustecosto_articulo_nro_docum_seq'::regclass) NOT NULL, 
	fec_doc DATE NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	observaciones VARCHAR(250), 
	imp_costo_actual NUMERIC(20, 2) NOT NULL, 
	imp_costo_nuevo NUMERIC(20, 2) NOT NULL, 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_ajustecosto_articulo_pk PRIMARY KEY (id_trans), 
	CONSTRAINT t_ajustecosto_articulo_unique UNIQUE NULLS DISTINCT (id_emp, nro_docum)
);

CREATE TABLE public.t_ajustestock (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	documento VARCHAR(10) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	id_calculo INTEGER NOT NULL, 
	fecha_movimiento DATE NOT NULL, 
	id_estado INTEGER NOT NULL, 
	id_motivo INTEGER NOT NULL, 
	observacion VARCHAR(250), 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_ajustestock_pk PRIMARY KEY (id_trans)
);

CREATE TABLE public.t_facturas (
	id_emp INTEGER NOT NULL, 
	id_trans INTEGER NOT NULL, 
	id_cliente INTEGER NOT NULL, 
	id_sucursal_emp INTEGER NOT NULL, 
	id_sucursal_cliente INTEGER NOT NULL, 
	fec_doc DATE NOT NULL, 
	documento VARCHAR(16) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	serie_docum VARCHAR(8) NOT NULL, 
	documento_ref VARCHAR(16) NOT NULL, 
	nro_ref INTEGER NOT NULL, 
	serie_ref VARCHAR(8) NOT NULL, 
	documento_remito VARCHAR(16) NOT NULL, 
	nro_remito INTEGER NOT NULL, 
	serie_remito VARCHAR(8) NOT NULL, 
	id_turno INTEGER, 
	observacion VARCHAR(250) NOT NULL, 
	imp_ingreso NUMERIC(14, 2), 
	imp_vuelto NUMERIC(14, 2), 
	fec_venc DATE, 
	id_moneda INTEGER, 
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	vista VARCHAR(16) NOT NULL, 
	signo INTEGER NOT NULL, 
	imp_neto NUMERIC(14, 2) NOT NULL, 
	tipo_dcto VARCHAR(10), 
	porc_dcto NUMERIC(6, 2) NOT NULL, 
	imp_descuento NUMERIC(14, 2) NOT NULL, 
	imp_total NUMERIC(14, 2) NOT NULL, 
	impuesto1 VARCHAR(6) NOT NULL, 
	valor_impuesto1 NUMERIC(14, 2) NOT NULL, 
	impuesto2 VARCHAR(6) NOT NULL, 
	valor_impuesto2 NUMERIC(14, 2) NOT NULL, 
	impuesto3 VARCHAR(6) NOT NULL, 
	valor_impuesto3 NUMERIC(14, 2) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	id_caja INTEGER, 
	CONSTRAINT t_facturas_pk PRIMARY KEY (id_emp, id_trans)
);

CREATE TABLE public.t_trasladobodega (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	documento VARCHAR(10) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	id_calculo INTEGER NOT NULL, 
	fecha_movimiento DATE NOT NULL, 
	id_bodega_origen INTEGER NOT NULL, 
	id_bodega_destino INTEGER NOT NULL, 
	id_estado_origen INTEGER NOT NULL, 
	id_estado_destino INTEGER NOT NULL, 
	observacion VARCHAR(250), 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_trasladobodega_pk PRIMARY KEY (id_trans)
);

CREATE TABLE public.td_ajustestock (
	id_trans BIGINT NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	id_ubicacion INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	cant_disp INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	CONSTRAINT td_ajustestock_pk PRIMARY KEY (id_trans, id_articulo, linea)
);

CREATE TABLE public.td_cargastock (
	id_trans BIGINT NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	id_ubicacion INTEGER NOT NULL, 
	costo NUMERIC(20, 2) NOT NULL, 
	cantidad INTEGER NOT NULL, 
	precio_venta NUMERIC(20, 2) NOT NULL, 
	CONSTRAINT td_cargastock_pk PRIMARY KEY (id_trans, id_articulo, linea)
);

CREATE TABLE public.td_compras (
	id_trans INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	ref_compras VARCHAR(100) NOT NULL, 
	costo_unit NUMERIC(14, 2) NOT NULL, 
	cantidad INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	stock INTEGER NOT NULL, 
	porc_dcto NUMERIC(6, 3), 
	impuesto1 VARCHAR(6) NOT NULL, 
	id_tasaimp1 INTEGER NOT NULL, 
	valor_impuesto1 NUMERIC(14, 2) NOT NULL, 
	impuesto2 VARCHAR(6) NOT NULL, 
	id_tasaimp2 INTEGER NOT NULL, 
	valor_impuesto2 NUMERIC(14, 2) NOT NULL, 
	impuesto3 VARCHAR(6) NOT NULL, 
	id_tasaimp3 INTEGER NOT NULL, 
	valor_impuesto3 NUMERIC(14, 2) NOT NULL, 
	costo_total NUMERIC(14, 2) NOT NULL, 
	imp_dcto NUMERIC(14, 2) NOT NULL, 
	importe NUMERIC(14, 2) NOT NULL, 
	CONSTRAINT td_compras_pk PRIMARY KEY (id_trans, linea)
);

CREATE TABLE public.td_comprasnewcodbarra (
	id_trans INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	cod_barra VARCHAR(50), 
	ref_barra VARCHAR(100), 
	CONSTRAINT td_comprasnewcodbarra_pk PRIMARY KEY (id_trans, id_articulo, id_codbarra)
);

CREATE TABLE public.td_facturas (
	id_emp INTEGER NOT NULL, 
	id_trans INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	precio_unit NUMERIC(14, 2) NOT NULL, 
	cantidad INTEGER NOT NULL, 
	stock INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	tipo_vta VARCHAR(2) NOT NULL, 
	impuesto1 VARCHAR(6) NOT NULL, 
	id_tasaimp1 INTEGER NOT NULL, 
	valor_impuesto1 NUMERIC(14, 2) NOT NULL, 
	impuesto2 VARCHAR(6) NOT NULL, 
	id_tasaimp2 INTEGER NOT NULL, 
	valor_impuesto2 NUMERIC(14, 2) NOT NULL, 
	impuesto3 VARCHAR(6) NOT NULL, 
	id_tasaimp3 INTEGER NOT NULL, 
	valor_impuesto3 NUMERIC(14, 2) NOT NULL, 
	imp_neto NUMERIC(14, 2) NOT NULL, 
	porc_dcto NUMERIC(6, 2) NOT NULL, 
	imp_dcto NUMERIC(14, 2) NOT NULL, 
	imp_total NUMERIC(14, 2) NOT NULL, 
	linea INTEGER NOT NULL, 
	referencia VARCHAR(100), 
	CONSTRAINT td_facturas_pk PRIMARY KEY (id_emp, id_trans, id_articulo, linea)
);

CREATE TABLE public.td_trasladobodega (
	id_trans BIGINT NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	id_ubicacion INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	cant_disp INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	CONSTRAINT td_trasladobodega_pk PRIMARY KEY (id_trans, id_articulo, linea)
);

CREATE TABLE public.m_conceptoscaja (
	id INTEGER DEFAULT nextval('m_conceptoscaja_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	nom_concepto VARCHAR(100), 
	signo INTEGER NOT NULL, 
	status BOOLEAN NOT NULL, 
	aplica_limit BOOLEAN, 
	imp_limit NUMERIC(14, 2), 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT m_conceptoscaja_pkey PRIMARY KEY (id), 
	CONSTRAINT m_conceptoscaja_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp)
);

CREATE TABLE public.m_departamentos (
	id_departamento INTEGER DEFAULT nextval('m_departamentos_id_departamento_seq'::regclass) NOT NULL, 
	id_pais INTEGER NOT NULL, 
	cod_dpto VARCHAR(10) NOT NULL, 
	nom_dpto VARCHAR(50) NOT NULL, 
	CONSTRAINT m_departamentos_pk PRIMARY KEY (id_departamento), 
	CONSTRAINT m_departamentos_id_pais_fkey FOREIGN KEY(id_pais) REFERENCES public.m_pais (id_pais)
);

CREATE TABLE public.m_impuesto (
	id INTEGER DEFAULT nextval('m_impuesto_id_seq'::regclass) NOT NULL, 
	id_tipo INTEGER, 
	tasa_impu VARCHAR(10) NOT NULL, 
	nombre_tasa VARCHAR(50) NOT NULL, 
	es_exenta VARCHAR(2) NOT NULL, 
	porc_tasa NUMERIC NOT NULL, 
	imp_minimo NUMERIC NOT NULL, 
	cuenta_vta VARCHAR(15) NOT NULL, 
	cuenta_cmp VARCHAR(15) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT impuestos_pk PRIMARY KEY (id), 
	CONSTRAINT fk_m_impuesto_empresa FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_impuesto_id_tipo_fkey FOREIGN KEY(id_tipo) REFERENCES public.m_tipoimpuesto (id), 
	CONSTRAINT impuestos_pk_unic UNIQUE NULLS DISTINCT (id_tipo, tasa_impu)
);

CREATE TABLE public.m_motivoajuste (
	id INTEGER DEFAULT nextval('m_motivoajuste_id_seq'::regclass) NOT NULL, 
	cod_motivo VARCHAR(10) NOT NULL, 
	nom_motivo VARCHAR(80) NOT NULL, 
	signo INTEGER NOT NULL, 
	activo VARCHAR(2) NOT NULL, 
	cta_inventario VARCHAR(15) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	logs JSON, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT m_motivoajuste_pk PRIMARY KEY (id), 
	CONSTRAINT fk_m_motivoajuste_empresa FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_motivoajuste_unique UNIQUE NULLS DISTINCT (cod_motivo)
);

CREATE TABLE public.m_motivodevolucion (
	id INTEGER DEFAULT nextval('m_motivodevolucion_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_motivo VARCHAR(10) NOT NULL, 
	nom_motivo VARCHAR(80) NOT NULL, 
	activo VARCHAR(2) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	logs JSON, 
	CONSTRAINT m_motivodevolucion_pk PRIMARY KEY (id), 
	CONSTRAINT m_motivodevolucion_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_motivodevolucion_unique UNIQUE NULLS DISTINCT (cod_motivo)
);

CREATE TABLE public.m_negocios (
	id INTEGER DEFAULT nextval('m_negocios_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_negocio VARCHAR(10) NOT NULL, 
	nom_negocio VARCHAR(100) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	activo BOOLEAN DEFAULT true NOT NULL, 
	CONSTRAINT m_negocios_pk PRIMARY KEY (id), 
	CONSTRAINT m_negocios_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_negocios_pk_unique UNIQUE NULLS DISTINCT (id_emp, cod_negocio)
);

CREATE TABLE public.m_personas (
	id_persona INTEGER DEFAULT nextval('m_personas_id_persona_seq'::regclass) NOT NULL, 
	id_tipodoc INTEGER NOT NULL, 
	cod_tit VARCHAR(50) NOT NULL, 
	nombres VARCHAR(60) NOT NULL, 
	apellidos VARCHAR(60) NOT NULL, 
	nombre_completo VARCHAR(120) NOT NULL, 
	sexo VARCHAR(2), 
	fec_nacimiento DATE, 
	direccion VARCHAR(50), 
	telefono VARCHAR(60), 
	mail VARCHAR(60), 
	id_ciudad INTEGER NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_personas_pk PRIMARY KEY (id_persona), 
	CONSTRAINT m_personas_id_tipodoc_fkey FOREIGN KEY(id_tipodoc) REFERENCES public.m_tipodocumentos (id), 
	CONSTRAINT m_personas_uniq UNIQUE NULLS DISTINCT (cod_tit)
);

CREATE TABLE public.m_subcategorias (
	id INTEGER DEFAULT nextval('m_subcategorias_id_seq'::regclass) NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	cod_subcategoria VARCHAR(20) NOT NULL, 
	nom_subcategoria VARCHAR(50), 
	CONSTRAINT m_subcategorias_pkey PRIMARY KEY (id), 
	CONSTRAINT m_subcategorias_categoria_id_fkey FOREIGN KEY(categoria_id) REFERENCES public.m_categorias (id), 
	CONSTRAINT m_subcategorias_cod_emp_cod_subcategoria_key UNIQUE NULLS DISTINCT (categoria_id, cod_subcategoria)
);

CREATE TABLE public.m_subcategoriasmodel (
	id INTEGER NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	cod_subcategoria VARCHAR(20) NOT NULL, 
	nom_subcategoria VARCHAR(50), 
	CONSTRAINT m_subcategoriasmodel_pjey PRIMARY KEY (id), 
	CONSTRAINT m_m_subcategoriasmodel_id_fkey FOREIGN KEY(categoria_id) REFERENCES public.m_categorias (id), 
	CONSTRAINT m_subcategorias_cod_emp_m_subcategoriasmodel_key UNIQUE NULLS DISTINCT (categoria_id, cod_subcategoria, linea)
);

CREATE TABLE public.m_sucursales (
	id INTEGER DEFAULT nextval('m_sucursales_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_sucursal VARCHAR(20) NOT NULL, 
	nom_sucursal VARCHAR(80) NOT NULL, 
	id_ciudad INTEGER NOT NULL, 
	direccion VARCHAR(60), 
	telefono VARCHAR(20), 
	activo BOOLEAN DEFAULT true NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_sucursales_pk PRIMARY KEY (id), 
	CONSTRAINT m_sucursales_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_sucursales_unique UNIQUE NULLS DISTINCT (id_emp, cod_sucursal)
);

CREATE TABLE public.m_tiposervicio (
	id INTEGER DEFAULT nextval('m_tiposervicio_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	cod_servicio VARCHAR(20) NOT NULL, 
	nom_servicio VARCHAR(50) NOT NULL, 
	id_costeo INTEGER, 
	CONSTRAINT m_tiposervicio_pkey PRIMARY KEY (id), 
	CONSTRAINT m_tiposervicio_id_costeo_fkey FOREIGN KEY(id_costeo) REFERENCES public.m_costeo (id)
);

CREATE TABLE public.m_unidades (
	id INTEGER DEFAULT nextval('m_unidades_id_seq'::regclass) NOT NULL, 
	cod_unidad VARCHAR(10) NOT NULL, 
	nom_unidad VARCHAR(50) NOT NULL, 
	es_paquete VARCHAR(2) NOT NULL, 
	convuni INTEGER NOT NULL, 
	logs JSONB, 
	fecha_mod DATE NOT NULL, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT m_unidades_pk PRIMARY KEY (id), 
	CONSTRAINT fk_m_unidades_empresa FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_unidades_pk_unica UNIQUE NULLS DISTINCT (id_emp, cod_unidad)
);

CREATE TABLE public.md_empresaxmodulo (
	id_emp INTEGER NOT NULL, 
	id_modulo INTEGER NOT NULL, 
	activo BOOLEAN DEFAULT true NOT NULL, 
	fecha_activacion DATE, 
	CONSTRAINT md_empresaxmodulo_pkey PRIMARY KEY (id_emp, id_modulo), 
	CONSTRAINT md_empresaxmodulo_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT md_empresaxmodulo_id_modulo_fkey FOREIGN KEY(id_modulo) REFERENCES public.md_modulo (id_modulo)
);

CREATE TABLE public.md_menu (
	id_menu INTEGER DEFAULT nextval('md_menu_id_menu_seq'::regclass) NOT NULL, 
	id_modulo INTEGER NOT NULL, 
	codigo VARCHAR(50) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion VARCHAR(250), 
	ruta VARCHAR(250), 
	icono VARCHAR(100), 
	id_padre INTEGER, 
	orden INTEGER DEFAULT 0 NOT NULL, 
	visible BOOLEAN DEFAULT true NOT NULL, 
	activo BOOLEAN DEFAULT true NOT NULL, 
	es_contenedor BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT md_menu_pkey PRIMARY KEY (id_menu), 
	CONSTRAINT fk_menu_modulo FOREIGN KEY(id_modulo) REFERENCES public.md_modulo (id_modulo), 
	CONSTRAINT fk_menu_padre FOREIGN KEY(id_padre) REFERENCES public.md_menu (id_menu), 
	CONSTRAINT md_menu_codigo_key UNIQUE NULLS DISTINCT (codigo)
);

CREATE TABLE public.md_numeradores (
	id_emp INTEGER NOT NULL, 
	codigo VARCHAR(30) NOT NULL, 
	ultimo_valor INTEGER DEFAULT 0 NOT NULL, 
	requiere_consecutivo BOOLEAN DEFAULT true NOT NULL, 
	CONSTRAINT md_numeradores_pk PRIMARY KEY (id_emp, codigo), 
	CONSTRAINT md_numeradores_empresa_fk FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp)
);

CREATE TABLE public.md_rol (
	id_rol INTEGER DEFAULT nextval('md_rol_id_rol_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	codigo VARCHAR(30) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion VARCHAR(250), 
	activo BOOLEAN DEFAULT true NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	logs JSON, 
	es_superadmin BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT md_rol_pkey PRIMARY KEY (id_rol), 
	CONSTRAINT md_rol_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT md_rol_codigo_emp_unique UNIQUE NULLS DISTINCT (id_emp, codigo)
);

CREATE TABLE public.p_movimientocajas (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	linea INTEGER NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_caja INTEGER NOT NULL, 
	id_mediopago INTEGER NOT NULL, 
	concepto VARCHAR(20) NOT NULL, 
	id_referencia INTEGER NOT NULL, 
	fec_doc DATE NOT NULL, 
	importe NUMERIC(20, 2) NOT NULL, 
	signo INTEGER NOT NULL, 
	vista VARCHAR(20) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT p_movimientocajas_pk PRIMARY KEY (id_trans, linea), 
	CONSTRAINT p_movimientocajas_id_caja_fkey FOREIGN KEY(id_caja) REFERENCES public.m_cajas (id), 
	CONSTRAINT p_movimientocajas_id_mediopago_fkey FOREIGN KEY(id_mediopago) REFERENCES public.m_mediopagos (id)
);

CREATE TABLE public.s_saldocaja (
	id_caja INTEGER NOT NULL, 
	id_mediopago INTEGER NOT NULL, 
	importe NUMERIC(20, 2) NOT NULL, 
	proceso VARCHAR(20) NOT NULL, 
	CONSTRAINT s_saldocaja_pk PRIMARY KEY (id_caja, id_mediopago), 
	CONSTRAINT s_saldocaja_id_caja_fkey FOREIGN KEY(id_caja) REFERENCES public.m_cajas (id), 
	CONSTRAINT s_saldocaja_id_mediopago_fkey FOREIGN KEY(id_mediopago) REFERENCES public.m_mediopagos (id)
);

CREATE TABLE public.t_abrirturno (
	id INTEGER NOT NULL, 
	id_caja INTEGER NOT NULL, 
	fec_doc DATE, 
	status BOOLEAN NOT NULL, 
	imp_base NUMERIC(14, 2), 
	usuario VARCHAR(16) NOT NULL, 
	observacion VARCHAR(100), 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	fecha_apertura TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT t_abrirturno_pkey PRIMARY KEY (id), 
	CONSTRAINT t_abrirturno_id_caja_fkey FOREIGN KEY(id_caja) REFERENCES public.m_cajas (id)
);

CREATE TABLE public.t_trasladocaja (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	documento VARCHAR(10) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	fecha_movimiento DATE NOT NULL, 
	id_caja_origen INTEGER NOT NULL, 
	id_mediopago_origen INTEGER NOT NULL, 
	id_caja_destino INTEGER NOT NULL, 
	id_mediopago_destino INTEGER NOT NULL, 
	importe NUMERIC(20, 2) NOT NULL, 
	observacion VARCHAR(250), 
	vista VARCHAR(20) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	logs JSON, 
	CONSTRAINT t_trasladocaja_pk PRIMARY KEY (id_trans), 
	CONSTRAINT t_trasladocaja_id_caja_destino_fkey FOREIGN KEY(id_caja_destino) REFERENCES public.m_cajas (id), 
	CONSTRAINT t_trasladocaja_id_caja_origen_fkey FOREIGN KEY(id_caja_origen) REFERENCES public.m_cajas (id), 
	CONSTRAINT t_trasladocaja_id_mediopago_destino_fkey FOREIGN KEY(id_mediopago_destino) REFERENCES public.m_mediopagos (id), 
	CONSTRAINT t_trasladocaja_id_mediopago_origen_fkey FOREIGN KEY(id_mediopago_origen) REFERENCES public.m_mediopagos (id)
);

CREATE TABLE public.td_ajustestocknuevolote (
	id_trans BIGINT NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	codigo_lote VARCHAR(50) NOT NULL, 
	fec_vencimiento DATE NOT NULL, 
	CONSTRAINT td_ajustestocknuevolote_pk PRIMARY KEY (id_trans, id_articulo, id_lote), 
	CONSTRAINT td_ajustestocknuevolote_fk FOREIGN KEY(id_trans) REFERENCES public.t_ajustestock (id_trans)
);

CREATE TABLE public.td_facturas_mediopago (
	id INTEGER DEFAULT nextval('td_facturas_mediopago_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_trans INTEGER NOT NULL, 
	linea INTEGER, 
	id_mediopago INTEGER NOT NULL, 
	importe NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	CONSTRAINT td_facturas_mediopago_pkey PRIMARY KEY (id), 
	CONSTRAINT td_facturas_mediopago_id_emp_id_trans_fkey FOREIGN KEY(id_emp, id_trans) REFERENCES public.t_facturas (id_emp, id_trans), 
	CONSTRAINT td_facturas_mediopago_id_mediopago_fkey FOREIGN KEY(id_mediopago) REFERENCES public.m_mediopagos (id), 
	CONSTRAINT td_facturas_mediopago_id_emp_id_trans_id_mediopago_key UNIQUE NULLS DISTINCT (id_emp, id_trans, id_mediopago)
);

CREATE TABLE public.m_articulos (
	id_articulo INTEGER DEFAULT nextval('m_articulos_id_articulo_seq'::regclass) NOT NULL, 
	cod_articulo VARCHAR(30) NOT NULL, 
	nom_articulo VARCHAR(100) NOT NULL, 
	id_negocio INTEGER NOT NULL, 
	id_categoria INTEGER NOT NULL, 
	id_subcategoria INTEGER NOT NULL, 
	activo_stock BOOLEAN NOT NULL, 
	stock_min INTEGER, 
	stock_max INTEGER, 
	id_ref INTEGER, 
	id_unidad INTEGER NOT NULL, 
	grupo_contable VARCHAR(20) NOT NULL, 
	id_tiposervicio INTEGER NOT NULL, 
	cta_inventario VARCHAR(15), 
	id_impuesto INTEGER, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	maneja_lote BOOLEAN DEFAULT false NOT NULL, 
	id_emp INTEGER NOT NULL, 
	CONSTRAINT m_articulos_pk PRIMARY KEY (id_articulo), 
	CONSTRAINT fk_m_articulos_empresa FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_articulos_id_impuesto_fkey FOREIGN KEY(id_impuesto) REFERENCES public.m_impuesto (id), 
	CONSTRAINT m_articulos_id_negocio_fkey FOREIGN KEY(id_negocio) REFERENCES public.m_negocios (id), 
	CONSTRAINT m_articulos_id_subcategoria_fkey FOREIGN KEY(id_subcategoria) REFERENCES public.m_subcategorias (id), 
	CONSTRAINT m_articulos_id_tiposervicio_fkey FOREIGN KEY(id_tiposervicio) REFERENCES public.m_tiposervicio (id), 
	CONSTRAINT m_articulos_id_unidad_fkey FOREIGN KEY(id_unidad) REFERENCES public.m_unidades (id), 
	CONSTRAINT m_articulos_unique UNIQUE NULLS DISTINCT (id_negocio, cod_articulo)
);

CREATE TABLE public.m_bodegas (
	id INTEGER DEFAULT nextval('m_bodegas_id_seq'::regclass) NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	cod_bodega VARCHAR(20) NOT NULL, 
	nom_bodega VARCHAR(80) NOT NULL, 
	principal VARCHAR(2) NOT NULL, 
	tiene_ubicaciones VARCHAR(2) NOT NULL, 
	activo VARCHAR(2) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_bodegas_pk PRIMARY KEY (id), 
	CONSTRAINT m_bodegas_id_sucursal_fkey FOREIGN KEY(id_sucursal) REFERENCES public.m_sucursales (id), 
	CONSTRAINT m_bodegas_unique UNIQUE NULLS DISTINCT (id_sucursal, cod_bodega)
);

CREATE TABLE public.m_ciudades (
	id_ciudad INTEGER DEFAULT nextval('m_ciudades_id_ciudad_seq'::regclass) NOT NULL, 
	id_departamento INTEGER NOT NULL, 
	cod_ciudad VARCHAR(10) NOT NULL, 
	nom_ciudad VARCHAR(50) NOT NULL, 
	CONSTRAINT m_ciudades_pk PRIMARY KEY (id_ciudad), 
	CONSTRAINT m_ciudades_id_departamento_fkey FOREIGN KEY(id_departamento) REFERENCES public.m_departamentos (id_departamento)
);

CREATE TABLE public.m_clientes (
	id_emp INTEGER NOT NULL, 
	id_cliente INTEGER DEFAULT nextval('m_clientes_id_cliente_seq'::regclass) NOT NULL, 
	id_persona INTEGER NOT NULL, 
	cod_tit VARCHAR(20) NOT NULL, 
	nom_cliente VARCHAR(100) NOT NULL, 
	activo BOOLEAN NOT NULL, 
	observacion VARCHAR(100) NOT NULL, 
	direccion VARCHAR(50) NOT NULL, 
	mail VARCHAR(60) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_clientes_pk PRIMARY KEY (id_cliente), 
	CONSTRAINT m_clientes_id_persona_fkey FOREIGN KEY(id_persona) REFERENCES public.m_personas (id_persona), 
	CONSTRAINT m_clientes_uniq UNIQUE NULLS DISTINCT (id_emp, cod_tit)
);

CREATE TABLE public.m_proveedores (
	id_emp INTEGER NOT NULL, 
	id_proveedor INTEGER DEFAULT nextval('m_proveedores_id_proveedor_seq'::regclass) NOT NULL, 
	id_persona INTEGER NOT NULL, 
	cod_tit VARCHAR(50) NOT NULL, 
	razon_social VARCHAR(150) NOT NULL, 
	regimen VARCHAR(20) NOT NULL, 
	observacion VARCHAR(250) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	activo BOOLEAN, 
	CONSTRAINT m_proveedores_pk PRIMARY KEY (id_proveedor), 
	CONSTRAINT m_proveedores_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT m_proveedores_id_persona_fkey FOREIGN KEY(id_persona) REFERENCES public.m_personas (id_persona), 
	CONSTRAINT m_proveedores_uniq UNIQUE NULLS DISTINCT (id_emp, cod_tit)
);

CREATE TABLE public.md_menu_permisos (
	id_menu_permiso INTEGER DEFAULT nextval('md_menu_permisos_id_menu_permiso_seq'::regclass) NOT NULL, 
	id_menu INTEGER NOT NULL, 
	id_permiso INTEGER NOT NULL, 
	CONSTRAINT md_menu_permisos_pkey PRIMARY KEY (id_menu_permiso), 
	CONSTRAINT md_menu_permisos_id_menu_fkey FOREIGN KEY(id_menu) REFERENCES public.md_menu (id_menu), 
	CONSTRAINT md_menu_permisos_id_permiso_fkey FOREIGN KEY(id_permiso) REFERENCES public.md_permisos (id_permiso), 
	CONSTRAINT md_menu_permisos_id_menu_id_permiso_key UNIQUE NULLS DISTINCT (id_menu, id_permiso)
);

CREATE TABLE public.md_menuxpermiso (
	id_menu INTEGER NOT NULL, 
	id_permiso INTEGER NOT NULL, 
	CONSTRAINT md_menuxpermiso_pkey PRIMARY KEY (id_menu, id_permiso), 
	CONSTRAINT md_menuxpermiso_id_menu_fkey FOREIGN KEY(id_menu) REFERENCES public.md_menu (id_menu), 
	CONSTRAINT md_menuxpermiso_id_permiso_fkey FOREIGN KEY(id_permiso) REFERENCES public.md_permiso (id_permiso)
);

CREATE TABLE public.md_rolxpermiso (
	id_rol INTEGER NOT NULL, 
	id_permiso INTEGER NOT NULL, 
	CONSTRAINT md_rolxpermiso_pkey PRIMARY KEY (id_rol, id_permiso), 
	CONSTRAINT md_rolxpermiso_id_permiso_fkey FOREIGN KEY(id_permiso) REFERENCES public.md_permiso (id_permiso), 
	CONSTRAINT md_rolxpermiso_id_rol_fkey FOREIGN KEY(id_rol) REFERENCES public.md_rol (id_rol)
);

CREATE TABLE public.md_usuarios (
	id_usuario INTEGER DEFAULT nextval('md_usuarios_id_usuario_seq'::regclass) NOT NULL, 
	id_persona INTEGER NOT NULL, 
	usuario VARCHAR(20) NOT NULL, 
	nom_usuario VARCHAR(100) NOT NULL, 
	clave VARCHAR(100) NOT NULL, 
	activo BOOLEAN, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_usuarios_pk PRIMARY KEY (id_usuario), 
	CONSTRAINT m_usuarios_pk_id_persona_fkey FOREIGN KEY(id_persona) REFERENCES public.m_personas (id_persona), 
	CONSTRAINT md_usuarios_usuario_unique UNIQUE NULLS DISTINCT (usuario)
);

CREATE TABLE public.t_cargastock (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	id_proveedor INTEGER NOT NULL, 
	documento VARCHAR(10) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	fecha_movimiento DATE NOT NULL, 
	observacion VARCHAR(250), 
	nombre_archivo VARCHAR(150), 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	id_negocio INTEGER NOT NULL, 
	CONSTRAINT t_cargastock_pk PRIMARY KEY (id_trans), 
	CONSTRAINT t_cargastock_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT t_cargastock_id_negocio_fkey FOREIGN KEY(id_negocio) REFERENCES public.m_negocios (id)
);

CREATE TABLE public.t_cierreturno (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_turno INTEGER NOT NULL, 
	fecha_cierre TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	observacion VARCHAR(250), 
	imp_base NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	imp_total NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	descuadre BOOLEAN DEFAULT false NOT NULL, 
	imp_descuadre NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	logs JSON, 
	CONSTRAINT t_cierreturno_pkey PRIMARY KEY (id_trans), 
	CONSTRAINT t_cierreturno_id_turno_fkey FOREIGN KEY(id_turno) REFERENCES public.t_abrirturno (id), 
	CONSTRAINT t_cierreturno_id_turno_key UNIQUE NULLS DISTINCT (id_turno)
);

CREATE TABLE public.t_movcajas (
	id INTEGER DEFAULT nextval('t_movcajas_id_seq'::regclass) NOT NULL, 
	id_concepto INTEGER NOT NULL, 
	id_turno INTEGER NOT NULL, 
	fecha DATE, 
	observacion VARCHAR(250), 
	importe NUMERIC(14, 2), 
	signo INTEGER, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_movcajas_pkey PRIMARY KEY (id), 
	CONSTRAINT t_movcajas_id_concepto_fkey FOREIGN KEY(id_concepto) REFERENCES public.m_conceptoscaja (id), 
	CONSTRAINT t_movcajas_id_turno_fkey FOREIGN KEY(id_turno) REFERENCES public.t_abrirturno (id)
);

CREATE TABLE public.td_abrirturno (
	id INTEGER DEFAULT nextval('td_abrirturno_id_seq'::regclass) NOT NULL, 
	id_turno INTEGER NOT NULL, 
	concepto VARCHAR(15) NOT NULL, 
	fecha TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	id_referencia INTEGER NOT NULL, 
	id_mediopago INTEGER NOT NULL, 
	importe NUMERIC(14, 2) NOT NULL, 
	signo INTEGER NOT NULL, 
	vista VARCHAR(16) NOT NULL, 
	CONSTRAINT td_abrirturno_id_mediopago_fkey FOREIGN KEY(id_mediopago) REFERENCES public.m_mediopagos (id), 
	CONSTRAINT td_abrirturno_id_turno_fkey FOREIGN KEY(id_turno) REFERENCES public.t_abrirturno (id)
);

CREATE TABLE public.m_artxcodigobarra (
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER DEFAULT nextval('m_artxcodigobarra_id_codbarra_seq'::regclass) NOT NULL, 
	cod_barra VARCHAR(50), 
	ref_barra VARCHAR(100), 
	estado BOOLEAN, 
	registro_nuevo BOOLEAN, 
	CONSTRAINT m_artxcodigobarra_pkey PRIMARY KEY (id_articulo, id_codbarra), 
	CONSTRAINT m_artxcodigobarra_id_articulo_fkey FOREIGN KEY(id_articulo) REFERENCES public.m_articulos (id_articulo)
);

CREATE TABLE public.m_artxcodigobarramodel (
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	cod_barra VARCHAR(50), 
	ref_barra VARCHAR(100), 
	estado BOOLEAN, 
	registro_nuevo BOOLEAN, 
	CONSTRAINT m_artxcodigobarramodel_pkey PRIMARY KEY (id_articulo, id_codbarra, linea), 
	CONSTRAINT m_artxcodigobarramodel_id_articulo_fkey FOREIGN KEY(id_articulo) REFERENCES public.m_articulos (id_articulo)
);

CREATE TABLE public.m_cajasxuser (
	id INTEGER DEFAULT nextval('m_cajasxuser_id_seq'::regclass) NOT NULL, 
	id_caja INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	CONSTRAINT m_cajasxuser_pkey PRIMARY KEY (id), 
	CONSTRAINT m_cajasxuser_id_caja_fkey FOREIGN KEY(id_caja) REFERENCES public.m_cajas (id), 
	CONSTRAINT m_cajasxuser_id_usuario_fkey FOREIGN KEY(id_usuario) REFERENCES public.md_usuarios (id_usuario)
);

CREATE TABLE public.m_conceptoscajaxuser (
	id INTEGER DEFAULT nextval('m_conceptoscajaxuser_id_seq'::regclass) NOT NULL, 
	id_concepto INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	CONSTRAINT m_conceptoscajaxuser_pkey PRIMARY KEY (id), 
	CONSTRAINT m_conceptoscajaxuser_id_concepto_fkey FOREIGN KEY(id_concepto) REFERENCES public.m_conceptoscaja (id), 
	CONSTRAINT m_conceptoscajaxuser_id_usuario_fkey FOREIGN KEY(id_usuario) REFERENCES public.md_usuarios (id_usuario)
);

CREATE TABLE public.m_lotes (
	id INTEGER DEFAULT nextval('m_lotes_id_seq'::regclass) NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	codigo_lote VARCHAR(20) NOT NULL, 
	fec_vencimiento DATE NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_lotes_pk PRIMARY KEY (id), 
	CONSTRAINT m_lotes_id_articulo_fkey FOREIGN KEY(id_articulo) REFERENCES public.m_articulos (id_articulo), 
	CONSTRAINT m_lotes_pk_unique UNIQUE NULLS DISTINCT (id_articulo, codigo_lote)
);

CREATE TABLE public.m_ubicaciones (
	id INTEGER DEFAULT nextval('m_ubicaciones_id_seq'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	cod_ubicacion VARCHAR(15) NOT NULL, 
	nom_ubicacion VARCHAR(50) NOT NULL, 
	logs JSON, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT m_ubicaciones_pk PRIMARY KEY (id), 
	CONSTRAINT m_ubicaciones_id_bodega_fkey FOREIGN KEY(id_bodega) REFERENCES public.m_bodegas (id), 
	CONSTRAINT m_ubicaciones_unique UNIQUE NULLS DISTINCT (id_emp, id_bodega, cod_ubicacion)
);

CREATE TABLE public.m_userxsucursal (
	id_sucursal INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	CONSTRAINT m_userxsucursal_pkey PRIMARY KEY (id_sucursal, id_usuario), 
	CONSTRAINT m_userxsucursal_id_sucursal_fkey FOREIGN KEY(id_sucursal) REFERENCES public.m_sucursales (id), 
	CONSTRAINT m_userxsucursal_id_usuario_fkey FOREIGN KEY(id_usuario) REFERENCES public.md_usuarios (id_usuario)
);

CREATE TABLE public.md_empresaxuser (
	id_usuario INTEGER NOT NULL, 
	id_emp INTEGER NOT NULL, 
	activo BOOLEAN DEFAULT true, 
	CONSTRAINT md_empresaxuser_pkey PRIMARY KEY (id_usuario, id_emp), 
	CONSTRAINT md_empresaxuser_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT md_empresaxuser_usuario_fkey FOREIGN KEY(id_usuario) REFERENCES public.md_usuarios (id_usuario)
);

CREATE TABLE public.md_rol_permiso (
	id_rol INTEGER NOT NULL, 
	id_menu_permiso INTEGER NOT NULL, 
	CONSTRAINT md_rol_permiso_pkey PRIMARY KEY (id_rol, id_menu_permiso), 
	CONSTRAINT md_rol_permiso_id_menu_permiso_fkey FOREIGN KEY(id_menu_permiso) REFERENCES public.md_menu_permisos (id_menu_permiso), 
	CONSTRAINT md_rol_permiso_id_rol_fkey FOREIGN KEY(id_rol) REFERENCES public.md_rol (id_rol)
);

CREATE TABLE public.md_usuarioxrol (
	id_usuario INTEGER NOT NULL, 
	id_rol INTEGER NOT NULL, 
	CONSTRAINT md_usuarioxrol_pkey PRIMARY KEY (id_usuario, id_rol), 
	CONSTRAINT md_usuarioxrol_id_rol_fkey FOREIGN KEY(id_rol) REFERENCES public.md_rol (id_rol), 
	CONSTRAINT md_usuarioxrol_usuario_fkey FOREIGN KEY(id_usuario) REFERENCES public.md_usuarios (id_usuario)
);

CREATE TABLE public.t_compras (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	id_proveedor INTEGER NOT NULL, 
	fec_doc DATE NOT NULL, 
	documento VARCHAR(16) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	remito VARCHAR(30) NOT NULL, 
	status VARCHAR(2) NOT NULL, 
	ingresa_bodega VARCHAR(2) NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	imp_neto NUMERIC(14, 2) NOT NULL, 
	imp_descuento NUMERIC(14, 2) NOT NULL, 
	imp_total NUMERIC(14, 2) NOT NULL, 
	observaciones VARCHAR(250) NOT NULL, 
	impuesto1 VARCHAR(6) NOT NULL, 
	valor_impuesto1 NUMERIC(14, 2) NOT NULL, 
	impuesto2 VARCHAR(6) NOT NULL, 
	valor_impuesto2 NUMERIC(14, 2) NOT NULL, 
	impuesto3 VARCHAR(6) NOT NULL, 
	valor_impuesto3 NUMERIC(14, 2) NOT NULL, 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_compras_pk PRIMARY KEY (id_trans), 
	CONSTRAINT t_compras_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT t_compras_id_proveedor_fkey FOREIGN KEY(id_proveedor) REFERENCES public.m_proveedores (id_proveedor), 
	CONSTRAINT t_compras_id_sucursal_fkey FOREIGN KEY(id_sucursal) REFERENCES public.m_sucursales (id), 
	CONSTRAINT t_compras_unique UNIQUE NULLS DISTINCT (id_emp, id_proveedor, remito)
);

CREATE TABLE public.td_cierreturno (
	id INTEGER DEFAULT nextval('td_cierreturno_id_seq'::regclass) NOT NULL, 
	id_cierre BIGINT NOT NULL, 
	concepto VARCHAR(15) NOT NULL, 
	id_mediopago INTEGER NOT NULL, 
	signo INTEGER NOT NULL, 
	importe_sistema NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	valor_usuario NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	diferencia NUMERIC(14, 2) DEFAULT 0 NOT NULL, 
	linea INTEGER, 
	CONSTRAINT td_cierreturno_pkey PRIMARY KEY (id), 
	CONSTRAINT td_cierreturno_id_cierre_fkey FOREIGN KEY(id_cierre) REFERENCES public.t_cierreturno (id_trans), 
	CONSTRAINT td_cierreturno_id_mediopago_fkey FOREIGN KEY(id_mediopago) REFERENCES public.m_mediopagos (id), 
	CONSTRAINT td_cierreturno_id_cierre_concepto_id_mediopago_signo_key UNIQUE NULLS DISTINCT (id_cierre, concepto, id_mediopago, signo)
);

CREATE TABLE public.t_devolucioncompras (
	id_trans BIGINT DEFAULT nextval('id_transaccion'::regclass) NOT NULL, 
	id_emp INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	id_proveedor INTEGER NOT NULL, 
	id_compra_origen BIGINT NOT NULL, 
	id_bodega INTEGER NOT NULL, 
	id_estado INTEGER NOT NULL, 
	fec_doc DATE NOT NULL, 
	documento VARCHAR(16) NOT NULL, 
	nro_docum INTEGER NOT NULL, 
	id_motivo INTEGER NOT NULL, 
	observacion VARCHAR(250) NOT NULL, 
	status VARCHAR(2) NOT NULL, 
	imp_total NUMERIC(14, 2) NOT NULL, 
	vista VARCHAR(16) NOT NULL, 
	fecha_mod TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	logs JSON, 
	CONSTRAINT t_devolucioncompras_pk PRIMARY KEY (id_trans), 
	CONSTRAINT t_devolucioncompras_id_bodega_fkey FOREIGN KEY(id_bodega) REFERENCES public.m_bodegas (id), 
	CONSTRAINT t_devolucioncompras_id_compra_origen_fkey FOREIGN KEY(id_compra_origen) REFERENCES public.t_compras (id_trans), 
	CONSTRAINT t_devolucioncompras_id_emp_fkey FOREIGN KEY(id_emp) REFERENCES public.md_empresas (id_emp), 
	CONSTRAINT t_devolucioncompras_id_motivo_fkey FOREIGN KEY(id_motivo) REFERENCES public.m_motivodevolucion (id), 
	CONSTRAINT t_devolucioncompras_id_proveedor_fkey FOREIGN KEY(id_proveedor) REFERENCES public.m_proveedores (id_proveedor), 
	CONSTRAINT t_devolucioncompras_id_sucursal_fkey FOREIGN KEY(id_sucursal) REFERENCES public.m_sucursales (id)
);

CREATE TABLE public.td_comprasnuevolote (
	id_trans BIGINT NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	linea INTEGER NOT NULL, 
	codigo_lote VARCHAR(50) NOT NULL, 
	fec_vencimiento DATE NOT NULL, 
	CONSTRAINT td_comprasnuevolote_pk PRIMARY KEY (id_trans, id_articulo, id_lote), 
	CONSTRAINT td_comprasnuevolote_fk FOREIGN KEY(id_trans) REFERENCES public.t_compras (id_trans)
);

CREATE TABLE public.td_devolucioncompras (
	id_trans BIGINT NOT NULL, 
	linea INTEGER NOT NULL, 
	id_articulo INTEGER NOT NULL, 
	id_codbarra INTEGER NOT NULL, 
	id_lote INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	costo_unit NUMERIC(14, 2) NOT NULL, 
	costo_total NUMERIC(14, 2) NOT NULL, 
	CONSTRAINT td_devolucioncompras_pk PRIMARY KEY (id_trans, linea), 
	CONSTRAINT td_devolucioncompras_id_trans_fkey FOREIGN KEY(id_trans) REFERENCES public.t_devolucioncompras (id_trans)
);

-- OWNERSHIP DE SECUENCIAS (solo las que son de una sola columna)
ALTER SEQUENCE public."m_articulos_id_articulo_seq" OWNED BY public."m_articulos"."id_articulo";
ALTER SEQUENCE public."m_artxcodigobarra_id_codbarra_seq" OWNED BY public."m_artxcodigobarra"."id_codbarra";
ALTER SEQUENCE public."m_bodegas_id_seq" OWNED BY public."m_bodegas"."id";
ALTER SEQUENCE public."m_cajas_id_seq" OWNED BY public."m_cajas"."id";
ALTER SEQUENCE public."m_cajasxuser_id_seq" OWNED BY public."m_cajasxuser"."id";
ALTER SEQUENCE public."m_categorias_id_seq" OWNED BY public."m_categorias"."id";
ALTER SEQUENCE public."m_ciudades_id_ciudad_seq" OWNED BY public."m_ciudades"."id_ciudad";
ALTER SEQUENCE public."m_clientes_id_cliente_seq" OWNED BY public."m_clientes"."id_cliente";
ALTER SEQUENCE public."m_conceptoscaja_id_seq" OWNED BY public."m_conceptoscaja"."id";
ALTER SEQUENCE public."m_conceptoscajaxuser_id_seq" OWNED BY public."m_conceptoscajaxuser"."id";
ALTER SEQUENCE public."m_costeo_id_seq" OWNED BY public."m_costeo"."id";
ALTER SEQUENCE public."m_departamentos_id_departamento_seq" OWNED BY public."m_departamentos"."id_departamento";
ALTER SEQUENCE public."m_empresa_id_emp_seq" OWNED BY public."md_empresas"."id_emp";
ALTER SEQUENCE public."m_estados_id_seq" OWNED BY public."m_estados"."id";
ALTER SEQUENCE public."m_impuesto_id_seq" OWNED BY public."m_impuesto"."id";
ALTER SEQUENCE public."m_lotes_id_seq" OWNED BY public."m_lotes"."id";
ALTER SEQUENCE public."m_mediopagos_id_seq" OWNED BY public."m_mediopagos"."id";
ALTER SEQUENCE public."m_motivoajuste_id_seq" OWNED BY public."m_motivoajuste"."id";
ALTER SEQUENCE public."m_motivodevolucion_id_seq" OWNED BY public."m_motivodevolucion"."id";
ALTER SEQUENCE public."m_negocios_id_seq" OWNED BY public."m_negocios"."id";
ALTER SEQUENCE public."m_pais_id_pais_seq" OWNED BY public."m_pais"."id_pais";
ALTER SEQUENCE public."m_personas_id_persona_seq" OWNED BY public."m_personas"."id_persona";
ALTER SEQUENCE public."m_proveedores_id_proveedor_seq" OWNED BY public."m_proveedores"."id_proveedor";
ALTER SEQUENCE public."m_subcategorias_id_seq" OWNED BY public."m_subcategorias"."id";
ALTER SEQUENCE public."m_sucursales_id_seq" OWNED BY public."m_sucursales"."id";
ALTER SEQUENCE public."m_tipodocumentos_id_seq" OWNED BY public."m_tipodocumentos"."id";
ALTER SEQUENCE public."m_tipoimpuesto_id_seq" OWNED BY public."m_tipoimpuesto"."id";
ALTER SEQUENCE public."m_tiposervicio_id_seq" OWNED BY public."m_tiposervicio"."id";
ALTER SEQUENCE public."m_ubicaciones_id_seq" OWNED BY public."m_ubicaciones"."id";
ALTER SEQUENCE public."m_unidades_id_seq" OWNED BY public."m_unidades"."id";
ALTER SEQUENCE public."md_menu_id_menu_seq" OWNED BY public."md_menu"."id_menu";
ALTER SEQUENCE public."md_menu_permisos_id_menu_permiso_seq" OWNED BY public."md_menu_permisos"."id_menu_permiso";
ALTER SEQUENCE public."md_modulo_id_modulo_seq" OWNED BY public."md_modulo"."id_modulo";
ALTER SEQUENCE public."md_permiso_id_permiso_seq" OWNED BY public."md_permiso"."id_permiso";
ALTER SEQUENCE public."md_permisos_id_permiso_seq" OWNED BY public."md_permisos"."id_permiso";
ALTER SEQUENCE public."md_rol_id_rol_seq" OWNED BY public."md_rol"."id_rol";
ALTER SEQUENCE public."md_usuarios_id_usuario_seq" OWNED BY public."md_usuarios"."id_usuario";
ALTER SEQUENCE public."t_ajustecosto_articulo_nro_docum_seq" OWNED BY public."t_ajustecosto_articulo"."nro_docum";
ALTER SEQUENCE public."t_movcajas_id_seq" OWNED BY public."t_movcajas"."id";
ALTER SEQUENCE public."td_abrirturno_id_seq" OWNED BY public."td_abrirturno"."id";
ALTER SEQUENCE public."td_cierreturno_id_seq" OWNED BY public."td_cierreturno"."id";
ALTER SEQUENCE public."td_facturas_mediopago_id_seq" OWNED BY public."td_facturas_mediopago"."id";

-- FUNCIONES
CREATE OR REPLACE FUNCTION public.articulo_obtener_stock_masivo(p_id_articulo integer, p_cadena_codigos text)
 RETURNS TABLE(idcodbarra integer, stock integer, movimientos integer)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY

    WITH Items_Separados AS (
        -- 1. Separamos por '-' para obtener el codigo de barra
        SELECT string_to_table(p_cadena_codigos, '-')::INTEGER AS codigo
    )
	select a.codigo,
	sum(COALESCE(B.cantidad, 0))::INTEGER stock,
	(select count(*) from p_stock where id_articulo=p_id_articulo and id_codbarra=a.codigo)::INTEGER movimientos 
	from Items_Separados A
	left join s_stkbodegas B on a.codigo=B.id_codbarra and B.id_articulo=p_id_articulo
	group by a.codigo;
	
END;
$function$
;

CREATE OR REPLACE FUNCTION public.comercial_turnos_ultimacaja(p_user character varying)
 RETURNS TABLE(idturno integer, fecha date, estado character varying)
 LANGUAGE plpgsql
AS $function$
DECLARE 
    v_cantidad_abiertas int;
    v_tiene_registros bool;
BEGIN

    -- 1. Verificamos si tiene turnos abiertos
    SELECT COUNT(id) INTO v_cantidad_abiertas 
    FROM t_abrirturno 
    WHERE usuario = p_user AND status = true;

    IF (v_cantidad_abiertas > 0) THEN 
        RETURN QUERY
        SELECT id as idturno, fec_doc as fecha, 'Abierta'::varchar(20) as estado 
        FROM t_abrirturno 
        WHERE usuario = p_user AND status = true;
    ELSE 
        -- 2. Si no tiene abiertos, verificamos si al menos tiene algún registro histórico
        SELECT EXISTS(SELECT 1 FROM t_abrirturno WHERE usuario = p_user) INTO v_tiene_registros;

        IF (v_tiene_registros) THEN
            -- Si tiene historial, devolvemos la última caja cerrada
            RETURN QUERY
            SELECT id as idturno, fec_doc as fecha, 'Cerrada'::varchar(20) as estado 
            FROM t_abrirturno 
            WHERE usuario = p_user 
              AND id = (SELECT MAX(id) FROM t_abrirturno WHERE usuario = p_user);
        ELSE
            -- Si el usuario no tiene NINGÚN registro, devolvemos los valores por defecto
            RETURN QUERY 
            SELECT 0 as idturno, now()::date as fecha, 'SinCaja'::varchar(20) as estado;
        END IF;

    END IF; 

END;
$function$
;

CREATE OR REPLACE FUNCTION public.compras_obtener_stock_costo_masivo(p_cadena_articulos text, p_id_bodega integer, p_id_estado integer)
 RETURNS TABLE(idarticulo integer, idcodbarra integer, stock integer, costo numeric)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
	--select * from compras_obtener_stock_costo_masivo('10-17;4-5;5-7',1,1)

    WITH Items_Separados AS (
        -- 1. Separamos por ';' para obtener cada pareja "idArticulo-idCodBarra"
        SELECT string_to_table(p_cadena_articulos, ';') AS pareja
    ),
    Items_Parsed AS (
        -- 2. Separamos por '-' para obtener los IDs individuales
        -- split_part(string, delimiter, n_elemento)
        SELECT 
            split_part(pareja, '-', 1)::INTEGER AS v_id_art,
            split_part(pareja, '-', 2)::INTEGER AS v_id_cod
        FROM Items_Separados
        WHERE pareja <> '' -- Evitamos cadenas vacías al final
    )
    -- 3. Hacemos el JOIN con inventarios y costos
    SELECT 
        A.v_id_art,
        A.v_id_cod,
        COALESCE(B.cantidad, 0)::INTEGER,
        COALESCE(C.imp_costo_unitario, 0)::NUMERIC
    FROM Items_Parsed A
	left join s_stkbodegas B ON B.id_bodega=p_id_bodega AND B.id_estado=p_id_estado AND B.id_articulo=A.v_id_art AND B.id_codbarra=A.v_id_cod
	left join s_costoxbodegas C ON C.id_bodega=p_id_bodega AND C.id_articulo=A.v_id_art;
	
END;
$function$
;

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
;

CREATE OR REPLACE FUNCTION public.monitorcompra_costo(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(negocio character varying, idbodega integer, bodega character varying, categoria character varying, subcategoria character varying, idarticulo integer, cod_articulo character varying, nom_articulo character varying, costo numeric)
 LANGUAGE plpgsql
AS $function$
    DECLARE
        v_sql TEXT;
    BEGIN
        v_sql := 'select
                COALESCE(G.nom_negocio,'''')					as Negocio,
                COALESCE(id_bodega,0)							as idbodega,
                COALESCE(CodigoBodega,''Sin Bodega'')			as NomBodega,
                COALESCE(E.nom_categoria,'''')					as categoria,
                COALESCE(F.nom_subcategoria,'''')				as subCategoria,
                COALESCE(a.id_articulo,0)						as idarticulo,
                a.cod_articulo                  				as CodArticulo,
                a.nom_articulo                 			    	as NomArticulo,
                COALESCE(B.imp_costo_unitario,0)				as Costo
                from m_articulos A
                left join (
                    SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                    A.id_articulo,A.imp_costo_unitario
                    FROM s_costoxbodegas A
                    INNER JOIN m_bodegas B on A.id_bodega=B.id) B on A.id_articulo=B.id_articulo
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
    $function$
;

CREATE OR REPLACE FUNCTION public.monitorcompras_detalle(param_id_trans bigint)
 RETURNS TABLE(cod_barra character varying, nom_articulo character varying, codigo_lote character varying, costo numeric, cantidad integer, neto numeric, porc_dcto numeric, importe_dcto numeric, porc_iva numeric, importe_iva numeric, total numeric)
 LANGUAGE sql
AS $function$
    SELECT
        COALESCE(CB.cod_barra, ''::varchar) AS cod_barra,
        A.nom_articulo,
        L.codigo_lote,
        D.costo_unit AS costo,
        D.cantidad,
        D.costo_total AS neto,
        D.porc_dcto,
        D.imp_dcto AS importe_dcto,
        COALESCE(I.porc_tasa, 0) AS porc_iva,
        COALESCE(D.valor_impuesto1, 0) AS importe_iva,
        D.importe AS total
    FROM td_compras D
    INNER JOIN m_articulos A ON D.id_articulo = A.id_articulo
    LEFT JOIN m_artxcodigobarra CB ON D.id_codbarra = CB.id_codbarra
    LEFT JOIN m_impuesto I ON D.id_tasaimp1 = I.id
    LEFT JOIN m_lotes L ON D.id_lote = L.id
    WHERE D.id_trans = param_id_trans
    ORDER BY D.linea
$function$
;

CREATE OR REPLACE FUNCTION public.monitorcompras_devoluciones(param_id_compra_origen bigint)
 RETURNS TABLE(nro_devolucion integer, fecha date, motivo character varying, cod_barra character varying, nom_articulo character varying, codigo_lote character varying, cantidad integer, costo_unit numeric, costo_total numeric)
 LANGUAGE sql
AS $function$
    SELECT
        T.nro_docum,
        T.fec_doc,
        M.nom_motivo,
        COALESCE(CB.cod_barra, ''::varchar) AS cod_barra,
        A.nom_articulo,
        L.codigo_lote,
        D.cantidad,
        D.costo_unit,
        D.costo_total
    FROM t_devolucioncompras T
    INNER JOIN td_devolucioncompras D ON T.id_trans = D.id_trans
    INNER JOIN m_articulos A ON D.id_articulo = A.id_articulo
    LEFT JOIN m_artxcodigobarra CB ON D.id_codbarra = CB.id_codbarra
    LEFT JOIN m_lotes L ON D.id_lote = L.id
    LEFT JOIN m_motivodevolucion M ON T.id_motivo = M.id
    WHERE T.id_compra_origen = param_id_compra_origen
    ORDER BY T.fec_doc DESC, T.nro_docum DESC, D.linea
$function$
;

CREATE OR REPLACE FUNCTION public.monitorcompras_kpi(param_id_emp integer, param_fecha_inicial date, param_fecha_final date, param_sucursal_id integer, param_bodega_id integer, param_proveedores integer[] DEFAULT NULL::integer[], param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totalremito integer, valorcomprado numeric)
 LANGUAGE plpgsql
AS $function$
    DECLARE
        v_sql TEXT;
    BEGIN
        -- Sin JOIN a td_compras: se usa EXISTS para el filtro de articulo,
        -- asi A no se multiplica por cada linea de detalle (evita el DISTINCT/GROUP BY)
        v_sql := 'SELECT cast(count(*) as integer), COALESCE(sum(A.imp_total), 0)
                  FROM t_compras A
                  WHERE A.id_emp = $1 AND A.fec_doc BETWEEN $2 AND $3';

        IF param_sucursal_id <> 0 THEN
            v_sql := v_sql || ' AND A.id_sucursal = ' || param_sucursal_id;
        END IF;

        IF param_bodega_id <> 0 THEN
            v_sql := v_sql || ' AND A.id_bodega = ' || param_bodega_id;
        END IF;

        v_sql := v_sql || ' AND ($4 IS NULL OR array_length($4,1) IS NULL OR A.id_proveedor = ANY($4))';
        -- EXISTS conserva el comportamiento original del INNER JOIN (exige al menos 1 linea de detalle)
        -- y ademas filtra por articulo cuando corresponde
        v_sql := v_sql || ' AND EXISTS (SELECT 1 FROM td_compras D WHERE D.id_trans = A.id_trans AND ($5 IS NULL OR array_length($5,1) IS NULL OR D.id_articulo = ANY($5)))';

        RETURN QUERY EXECUTE v_sql USING param_id_emp, param_fecha_inicial, param_fecha_final, param_proveedores, param_articulos;
    END;
    $function$
;

CREATE OR REPLACE FUNCTION public.monitorcompras_kpi_costos(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totalarticulos integer)
 LANGUAGE plpgsql
AS $function$
    DECLARE
        v_sql TEXT;
    BEGIN
        v_sql := 'select cast(count(A.id_articulo) as integer) totalarticulos from
                    m_articulos A
                    left join (SELECT A.id_bodega,B.cod_bodega,B.nom_bodega,B.nom_bodega as CodigoBodega,
                                A.id_articulo
                                FROM s_costoxbodegas A
                                INNER JOIN m_bodegas B on A.id_bodega=B.id) B on A.id_articulo=B.id_articulo
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
    $function$
;

CREATE OR REPLACE FUNCTION public.monitorcompras_vista1(param_id_emp integer, param_fecha_inicial date, param_fecha_final date, param_sucursal_id integer, param_bodega_id integer, param_limit integer, param_pagina integer, param_proveedores integer[] DEFAULT NULL::integer[], param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(id_trans bigint, fecha date, numoc integer, remito character varying, nombreproveedor character varying, nombrebodega character varying, importe numeric, num_devoluciones integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'SELECT A.id_trans, A.fec_doc, A.nro_docum, A.remito, P.razon_social, B.nom_bodega, A.imp_total,
                COALESCE(DEV.num_devoluciones, 0)::integer
              FROM t_compras A
              INNER JOIN m_proveedores P ON A.id_proveedor = P.id_proveedor
              INNER JOIN m_bodegas B ON A.id_bodega = B.id
              LEFT JOIN (SELECT id_compra_origen, COUNT(*) as num_devoluciones FROM t_devolucioncompras GROUP BY id_compra_origen) DEV ON DEV.id_compra_origen = A.id_trans
              WHERE A.id_emp = $1 AND A.fec_doc BETWEEN $2 AND $3';

    IF param_sucursal_id <> 0 THEN
        v_sql := v_sql || ' AND A.id_sucursal = ' || param_sucursal_id;
    END IF;

    IF param_bodega_id <> 0 THEN
        v_sql := v_sql || ' AND A.id_bodega = ' || param_bodega_id;
    END IF;

    v_sql := v_sql || ' AND ($4 IS NULL OR array_length($4,1) IS NULL OR A.id_proveedor = ANY($4))';
    v_sql := v_sql || ' AND EXISTS (SELECT 1 FROM td_compras D WHERE D.id_trans = A.id_trans AND ($5 IS NULL OR array_length($5,1) IS NULL OR D.id_articulo = ANY($5)))';

    IF param_incluir_limite THEN
        v_sql := v_sql || ' ORDER BY A.id_trans DESC LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
    ELSE
        v_sql := v_sql || ' ORDER BY A.id_trans DESC';
    END IF;

    RETURN QUERY EXECUTE v_sql USING param_id_emp, param_fecha_inicial, param_fecha_final, param_proveedores, param_articulos;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitoroperaciones_ventas_kpi(param_id_emp integer, param_fecha_inicial date, param_fecha_final date, param_sucursal_id integer, param_caja_id integer, param_tipos_documento text[] DEFAULT NULL::text[], param_solo_con_descuento boolean DEFAULT false, param_clientes integer[] DEFAULT NULL::integer[], param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totalventas integer, valorvendido numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'SELECT cast(count(*) as integer), COALESCE(sum(A.imp_total), 0)
              FROM t_facturas A
              LEFT JOIN m_documventas MD ON MD.id_emp = A.id_emp AND MD.id_sucursal_emp = A.id_sucursal_emp AND MD.documento = A.documento
              WHERE A.id_emp = $1 AND A.fec_doc BETWEEN $2 AND $3';

    IF param_sucursal_id <> 0 THEN
        v_sql := v_sql || ' AND A.id_sucursal_emp = ' || param_sucursal_id;
    END IF;

    IF param_caja_id <> 0 THEN
        v_sql := v_sql || ' AND (A.id_caja = ' || param_caja_id || ' OR EXISTS (SELECT 1 FROM t_abrirturno T WHERE T.id = A.id_turno AND T.id_caja = ' || param_caja_id || '))';
    END IF;

    IF param_solo_con_descuento THEN
        v_sql := v_sql || ' AND A.imp_descuento > 0';
    END IF;

    v_sql := v_sql || ' AND ($4 IS NULL OR array_length($4,1) IS NULL OR COALESCE(MD.clase_docum, ''Sin Clasificar'') = ANY($4))';
    v_sql := v_sql || ' AND ($5 IS NULL OR array_length($5,1) IS NULL OR A.id_cliente = ANY($5))';
    v_sql := v_sql || ' AND EXISTS (SELECT 1 FROM td_facturas D WHERE D.id_emp = A.id_emp AND D.id_trans = A.id_trans AND ($6 IS NULL OR array_length($6,1) IS NULL OR D.id_articulo = ANY($6)))';

    RETURN QUERY EXECUTE v_sql USING param_id_emp, param_fecha_inicial, param_fecha_final, param_tipos_documento, param_clientes, param_articulos;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitoroperaciones_ventas_vista1(param_id_emp integer, param_fecha_inicial date, param_fecha_final date, param_sucursal_id integer, param_caja_id integer, param_limit integer, param_pagina integer, param_tipos_documento text[] DEFAULT NULL::text[], param_solo_con_descuento boolean DEFAULT false, param_clientes integer[] DEFAULT NULL::integer[], param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(id_trans integer, nombre_sucursal character varying, tipo_documento character varying, factura text, fecha date, nombre_cliente character varying, nombre_caja character varying, importe numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'SELECT A.id_trans, S.nom_sucursal, COALESCE(MD.clase_docum, ''Sin Clasificar''), A.serie_docum || A.nro_docum::text, A.fec_doc, C.nom_cliente,
                CJ.nom_caja, A.imp_total
              FROM t_facturas A
              INNER JOIN m_sucursales S ON S.id = A.id_sucursal_emp
              INNER JOIN m_clientes C ON C.id_cliente = A.id_cliente
              LEFT JOIN m_documventas MD ON MD.id_emp = A.id_emp AND MD.id_sucursal_emp = A.id_sucursal_emp AND MD.documento = A.documento
              LEFT JOIN m_cajas CJ ON CJ.id = COALESCE((SELECT T.id_caja FROM t_abrirturno T WHERE T.id = A.id_turno), A.id_caja)
              WHERE A.id_emp = $1 AND A.fec_doc BETWEEN $2 AND $3';

    IF param_sucursal_id <> 0 THEN
        v_sql := v_sql || ' AND A.id_sucursal_emp = ' || param_sucursal_id;
    END IF;

    IF param_caja_id <> 0 THEN
        v_sql := v_sql || ' AND (A.id_caja = ' || param_caja_id || ' OR EXISTS (SELECT 1 FROM t_abrirturno T WHERE T.id = A.id_turno AND T.id_caja = ' || param_caja_id || '))';
    END IF;

    IF param_solo_con_descuento THEN
        v_sql := v_sql || ' AND A.imp_descuento > 0';
    END IF;

    v_sql := v_sql || ' AND ($4 IS NULL OR array_length($4,1) IS NULL OR COALESCE(MD.clase_docum, ''Sin Clasificar'') = ANY($4))';
    v_sql := v_sql || ' AND ($5 IS NULL OR array_length($5,1) IS NULL OR A.id_cliente = ANY($5))';
    v_sql := v_sql || ' AND EXISTS (SELECT 1 FROM td_facturas D WHERE D.id_emp = A.id_emp AND D.id_trans = A.id_trans AND ($6 IS NULL OR array_length($6,1) IS NULL OR D.id_articulo = ANY($6)))';

    IF param_incluir_limite THEN
        v_sql := v_sql || ' ORDER BY A.id_trans DESC LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
    ELSE
        v_sql := v_sql || ' ORDER BY A.id_trans DESC';
    END IF;

    RETURN QUERY EXECUTE v_sql USING param_id_emp, param_fecha_inicial, param_fecha_final, param_tipos_documento, param_clientes, param_articulos;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_kardex(param_id_articulo integer, param_id_codbarra integer, param_fecha_inicial date, param_fecha_final date)
 RETURNS TABLE(fec_doc date, documento character varying, nro_docum integer, bodega character varying, estado character varying, tipo_movimiento character varying, cantidad integer, vista character varying)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        P.fec_doc,
        P.documento,
        P.nro_docum,
        COALESCE(B.nom_bodega, 'Sin Bodega')::character varying as bodega,
        COALESCE(E.cod_estado, '')::character varying as estado,
        CASE WHEN P.signo >= 0 THEN 'Entrada' ELSE 'Salida' END::character varying as tipo_movimiento,
        P.cantidad,
        P.vista
    FROM p_stock P
    LEFT JOIN m_bodegas B ON P.id_bodega = B.id
    LEFT JOIN m_estados E ON P.id_estado = E.id
    WHERE P.id_articulo = param_id_articulo
      AND P.id_codbarra = param_id_codbarra
      AND (param_fecha_inicial IS NULL OR P.fec_doc >= param_fecha_inicial)
      AND (param_fecha_final IS NULL OR P.fec_doc <= param_fecha_final)
    ORDER BY P.fec_doc, P.id_trans;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
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
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_stockminimo_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totalarticulos integer, totalfaltante numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'select cast(count(*) as integer) totalarticulos, COALESCE(SUM(A.stock_min - COALESCE(B.cantidad,0)),0) as totalfaltante
			from m_articulos A
			left join (
				SELECT id_articulo, SUM(cantidad) as cantidad
				FROM s_stkbodegas
				WHERE 1=1 AND id_emp = ' || param_id_emp;

    IF param_bodega_id <> 0 THEN
        v_sql := v_sql || ' AND id_bodega = ' || param_bodega_id;
    END IF;

    v_sql := v_sql || ' GROUP BY id_articulo
			) B on A.id_articulo = B.id_articulo
			where A.stock_min > 0 AND COALESCE(B.cantidad,0) < A.stock_min';

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
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_stockminimo_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(negocio character varying, categoria character varying, subcategoria character varying, id_articulo integer, cod_articulo character varying, nom_articulo character varying, unidad character varying, cantidad_disponible integer, stock_minimo integer, stock_maximo integer, faltante integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'select
			COALESCE(G.nom_negocio,'''')				as Negocio,
			COALESCE(E.nom_categoria,'''')				as Categoria,
			COALESCE(F.nom_subcategoria,'''')			as SubCategoria,
			A.id_articulo								as IdArticulo,
			A.cod_articulo								as CodArticulo,
			A.nom_articulo								as NomArticulo,
			D.cod_unidad								as Unidad,
			COALESCE(B.cantidad,0)						as CantidadDisponible,
			A.stock_min									as StockMinimo,
			A.stock_max									as StockMaximo,
			(A.stock_min - COALESCE(B.cantidad,0))		as Faltante
			from m_articulos A
			left join (
				SELECT id_articulo, CAST(SUM(cantidad) as integer) as cantidad
				FROM s_stkbodegas
				WHERE 1=1 AND id_emp = ' || param_id_emp;

    IF param_bodega_id <> 0 THEN
        v_sql := v_sql || ' AND id_bodega = ' || param_bodega_id;
    END IF;

    v_sql := v_sql || ' GROUP BY id_articulo
			) B on A.id_articulo = B.id_articulo
			left join m_unidades D on A.id_unidad=D.id
			left join m_categorias E on A.id_categoria=E.id
			left join m_subcategorias F on A.id_subcategoria=F.id
			left join m_negocios G on A.id_negocio=G.id
			where A.stock_min > 0 AND COALESCE(B.cantidad,0) < A.stock_min';

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
        v_sql := v_sql || ' ORDER BY Faltante DESC LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
    ELSE
        v_sql := v_sql || ' ORDER BY Faltante DESC';
    END IF;

    RETURN QUERY EXECUTE v_sql USING param_articulos;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_valoracion_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totalarticulos integer, valortotal numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'select cast(count(*) as integer) totalarticulos, COALESCE(SUM(B.cantidad * B.imp_costo_unitario),0) as valortotal
			from m_articulos A
			left join (SELECT A.id_bodega, B.cod_bodega, B.nom_bodega, B.nom_bodega as CodigoBodega,
			A.id_articulo, A.cantidad, A.imp_costo_unitario
			FROM s_costoxbodegas A
			INNER JOIN m_bodegas B on A.id_bodega=B.id) B on A.id_articulo=B.id_articulo
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
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_valoracion_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(negocio character varying, bodega character varying, categoria character varying, subcategoria character varying, id_articulo integer, cod_articulo character varying, nom_articulo character varying, unidad character varying, cantidad integer, costo_unitario numeric, valor_total numeric)
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
			D.cod_unidad									as Unidad,
			COALESCE(B.cantidad,0)         					as Cantidad,
			COALESCE(B.imp_costo_unitario,0)					as CostoUnitario,
			COALESCE(B.cantidad * B.imp_costo_unitario,0)		as ValorTotal
			from m_articulos A
			left join (
				SELECT A.id_bodega, B.cod_bodega, B.nom_bodega, B.nom_bodega as CodigoBodega,
				A.id_articulo, A.cantidad, A.imp_costo_unitario
				FROM s_costoxbodegas A
				INNER JOIN m_bodegas B on A.id_bodega=B.id) B on A.id_articulo=B.id_articulo
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
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_vencimientos_kpi(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_articulos integer[] DEFAULT NULL::integer[])
 RETURNS TABLE(totallotes integer, totalunidades numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'select cast(count(*) as integer) totallotes, COALESCE(SUM(S.cantidad),0) as totalunidades
			from m_articulos A
			inner join m_lotes L on A.id_articulo = L.id_articulo
			inner join (
				SELECT id_bodega, id_articulo, id_lote, SUM(cantidad) as cantidad
				FROM s_stkbodegaxlote
				WHERE id_emp = ' || param_id_emp;

    IF param_bodega_id <> 0 THEN
        v_sql := v_sql || ' AND id_bodega = ' || param_bodega_id;
    END IF;

    v_sql := v_sql || ' GROUP BY id_bodega, id_articulo, id_lote
			) S on L.id_articulo = S.id_articulo AND L.id = S.id_lote
			left join m_negocios G on A.id_negocio=G.id
			where G.id_emp = ' || param_id_emp || '
			AND S.cantidad > 0
			AND L.fec_vencimiento <= (CURRENT_DATE + 30)';

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
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_vencimientos_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
 RETURNS TABLE(negocio character varying, categoria character varying, subcategoria character varying, id_articulo integer, cod_articulo character varying, nom_articulo character varying, bodega character varying, codigo_lote character varying, fec_vencimiento date, dias_para_vencer integer, cantidad integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := 'select
			COALESCE(G.nom_negocio,'''')				as Negocio,
			COALESCE(E.nom_categoria,'''')				as Categoria,
			COALESCE(F.nom_subcategoria,'''')			as SubCategoria,
			A.id_articulo								as IdArticulo,
			A.cod_articulo								as CodArticulo,
			A.nom_articulo								as NomArticulo,
			COALESCE(Bod.nom_bodega,''Sin Bodega'')	as Bodega,
			L.codigo_lote								as CodigoLote,
			L.fec_vencimiento							as FecVencimiento,
			CAST(L.fec_vencimiento - CURRENT_DATE as integer)	as DiasParaVencer,
			S.cantidad									as Cantidad
			from m_articulos A
			inner join m_lotes L on A.id_articulo = L.id_articulo
			inner join (
				SELECT id_bodega, id_articulo, id_lote, CAST(SUM(cantidad) as integer) as cantidad
				FROM s_stkbodegaxlote
				WHERE id_emp = ' || param_id_emp;

    IF param_bodega_id <> 0 THEN
        v_sql := v_sql || ' AND id_bodega = ' || param_bodega_id;
    END IF;

    v_sql := v_sql || ' GROUP BY id_bodega, id_articulo, id_lote
			) S on L.id_articulo = S.id_articulo AND L.id = S.id_lote
			left join m_bodegas Bod on S.id_bodega = Bod.id
			left join m_categorias E on A.id_categoria=E.id
			left join m_subcategorias F on A.id_subcategoria=F.id
			left join m_negocios G on A.id_negocio=G.id
			where G.id_emp = ' || param_id_emp || '
			AND S.cantidad > 0
			AND L.fec_vencimiento <= (CURRENT_DATE + 30)';

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
        v_sql := v_sql || ' ORDER BY L.fec_vencimiento ASC LIMIT ' || param_limit || ' OFFSET ' || param_pagina;
    ELSE
        v_sql := v_sql || ' ORDER BY L.fec_vencimiento ASC';
    END IF;

    RETURN QUERY EXECUTE v_sql USING param_articulos;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.monitorstock_vista1(param_id_emp integer, param_bodega_id integer, param_negocio_id integer, param_categoria_id integer, param_subcategoria_id integer, param_limit integer, param_pagina integer, param_articulos integer[] DEFAULT NULL::integer[], param_incluir_limite boolean DEFAULT true)
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
$function$
;

CREATE OR REPLACE FUNCTION public.p_costos_delete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    CALL public.sp_costeo_impacto_costeoxbodega('B', OLD.id_trans, OLD.linea);
    RETURN OLD;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.p_costos_insert()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN

	-- Impacto costo x bodega
	CALL public.sp_costeo_impacto_costeoxbodega( 'N',
        NEW.id_trans,
        NEW.linea);

    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.p_movimientocajas_delete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    CALL public.sp_caja_impacto_saldocaja('B', OLD.id_trans, OLD.linea);
    RETURN OLD;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.p_movimientocajas_insert()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    CALL public.sp_caja_impacto_saldocaja('N', NEW.id_trans, NEW.linea);
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.p_stock_delete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Impacto saldo x estado
    CALL public.sp_stock_impacto_stkestados('B',OLD.id_trans,OLD.linea);

	-- Impacto saldo x bodega
	CALL public.sp_stock_impacto_stkbodegas('B',OLD.id_trans,OLD.linea);

	-- Impacto saldo x bodega y lote
	CALL public.sp_stock_impacto_stkbodegaxlote('B',OLD.id_trans,OLD.linea);

   RETURN OLD;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.p_stock_insert()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Impacto saldo x estado
    CALL public.sp_stock_impacto_stkestados(
        'N',
        NEW.id_trans,
        NEW.linea
    );

	-- Impacto saldo x bodega
	CALL public.sp_stock_impacto_stkbodegas( 'N',
        NEW.id_trans,
        NEW.linea);

	-- Impacto saldo x bodega y lote
	CALL public.sp_stock_impacto_stkbodegaxlote( 'N',
        NEW.id_trans,
        NEW.linea);

    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.reporte_inventarioxbodega(bodega_id integer)
 RETURNS TABLE(bodega text, cod_articulo character varying, nom_articulo character varying, estado character varying, unidad character varying, cantidad integer)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	v_bodegaPrincipal text;
BEGIN
	--Cargamos la bodga principal
	select cod_bodega||'-'||nom_bodega
	INTO 
		v_bodegaPrincipal
	from m_bodegas where principal='S';
	
	
	RETURN QUERY
	select 
	COALESCE(CodigoBodega,v_bodegaPrincipal)		as NomBodega,   
	a.cod_articulo                  				as CodArticulo,    
	a.nom_articulo                 			    as NomArticulo,  
	COALESCE(c.cod_estado,'')						as Estado,		 
	D.cod_unidad									as Unidad,
	COALESCE(B.cantidad,0)         				as Cantidad
	from m_articulos A
	left join (
		SELECT B.cod_bodega,B.nom_bodega,(B.cod_bodega||'-'||B.nom_bodega) as CodigoBodega,A.id_articulo,A.id_estado,A.cantidad FROM s_stkbodegas A
		INNER JOIN m_bodegas B on A.id_bodega=A.id_bodega) B on A.id_articulo=B.id_articulo
	left join m_estados C on B.id_estado=C.id
	left join m_unidades D on A.id_unidad=D.id;

END
$function$
;

CREATE OR REPLACE PROCEDURE public.sp_ajustecostos(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
	--Borramos Costos
	delete from p_costos where id_trans=parm_trans;

	--Insertamos costos
	INSERT INTO public.p_costos(
	id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc, 
	id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo, 
	imp_costo_total, imp_costo_unitario, vista, fecha_mod)	
	select A.id_trans,1 linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,0 id_proveedor,A.fec_doc,
	a.id_articulo,0 cantidad,1 signo,imp_costo_actual,imp_costo_nuevo,0 imp_costo_adicional,
	B.cantidad stock_actual,
	B.cantidad stock_nuevo,
	cast((imp_costo_nuevo*B.cantidad) as numeric(20,2)) imp_costo_total,
	imp_costo_nuevo imp_costo_unitario,
	A.vista,A.fecha_mod	
	from t_ajustecosto_articulo A
	left join (select id_bodega,id_articulo,sum(cantidad) cantidad from s_stkbodegas
				group by id_bodega,id_articulo) B on A.id_bodega=B.id_bodega and A.id_articulo=B.id_articulo 
	where A.id_trans=parm_trans;


END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_articulo_updatecodigosbarra(IN p_id_articulo integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    -- Proceso que se usa en la edicion del articulo , cumple la funcion de editar los codigos de barra
	-- Teniendo encuenta los codigos nuevos , los codigos a elimnar y la actualizacion de datos para los codigos ya existentes

    -- 1. Eliminamos los códigos que ya no están en el modelo temporal
    DELETE FROM m_artxcodigobarra t
    WHERE t.id_articulo = p_id_articulo
    AND NOT EXISTS (
        SELECT 1 FROM m_artxcodigobarramodel m 
        WHERE m.id_articulo = p_id_articulo 
        AND m.id_codbarra = t.id_codbarra
    );
    
    -- 2. Actualizamos códigos existentes
    -- Nota: En el UPDATE de Postgres, la tabla destino no va en el FROM
    UPDATE m_artxcodigobarra t
    SET 
        cod_barra = m.cod_barra,
        ref_barra = m.ref_barra,
        estado = m.estado,
        registro_nuevo = false
    FROM m_artxcodigobarramodel m
    WHERE t.id_articulo = m.id_articulo
    AND t.id_codbarra = m.id_codbarra
    AND t.id_articulo = p_id_articulo;

    -- 3. Insertamos los registros nuevos
    -- Filtramos por id_codbarra = 0 (los que marcamos en FastAPI)
    INSERT INTO public.m_artxcodigobarra (
        id_articulo, cod_barra, ref_barra, estado, registro_nuevo
    )
    SELECT 
        m.id_articulo, m.cod_barra, m.ref_barra, m.estado, false::boolean -- ya no es nuevo una vez en la tabla final
    FROM m_artxcodigobarramodel m
    WHERE m.id_articulo = p_id_articulo 
    AND (m.id_codbarra = 0 OR m.registro_nuevo = true)
    AND NOT EXISTS (
        SELECT 1 FROM m_artxcodigobarra t 
        WHERE t.id_articulo = p_id_articulo 
        AND t.cod_barra = m.cod_barra
    );

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_caja_impacto_saldocaja(IN operacion character varying, IN parm_trans bigint, IN parm_linea integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    IF (operacion IN ('N')) THEN
        IF EXISTS (
            SELECT 1
            FROM p_movimientocajas A
            INNER JOIN s_saldocaja B
                ON A.id_caja = B.id_caja
                AND A.id_mediopago = B.id_mediopago
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea
        ) THEN
            UPDATE s_saldocaja SET
                importe = s_saldocaja.importe + (A.importe * A.signo)
            FROM p_movimientocajas A
            WHERE A.id_caja = s_saldocaja.id_caja
                AND A.id_mediopago = s_saldocaja.id_mediopago
                AND A.id_trans = parm_trans
                AND A.linea = parm_linea;
        ELSE
            INSERT INTO s_saldocaja (id_caja, id_mediopago, importe, proceso)
            SELECT
                A.id_caja,
                A.id_mediopago,
                (A.importe * A.signo),
                A.vista
            FROM p_movimientocajas A
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea;
        END IF;
    ELSE -- Operacion Borrar
        UPDATE s_saldocaja SET
            importe = s_saldocaja.importe - (A.importe * A.signo)
        FROM p_movimientocajas A
        WHERE A.id_caja = s_saldocaja.id_caja
            AND A.id_mediopago = s_saldocaja.id_mediopago
            AND A.id_trans = parm_trans
            AND A.linea = parm_linea;
    END IF;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_caja_impacto_trasladocajas(IN operacion character varying, IN parm_trans bigint)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    -- Borramos movimiento previo (si existe, por edicion) -- mismo patron idempotente que sp_compradirecta
    DELETE FROM p_movimientocajas WHERE id_trans = parm_trans;

    -- Insertamos las 2 patas del traslado: salida en origen, entrada en destino
    INSERT INTO p_movimientocajas
        (id_trans, linea, id_emp, id_caja, id_mediopago, concepto, id_referencia, fec_doc, importe, signo, vista, fecha_mod)
    SELECT id_trans, 1, id_emp, id_caja_origen, id_mediopago_origen, 'TrasladoCaja', id_trans, fecha_movimiento, importe, -1, vista, fecha_mod
    FROM t_trasladocaja WHERE id_trans = parm_trans
    UNION ALL
    SELECT id_trans, 2, id_emp, id_caja_destino, id_mediopago_destino, 'TrasladoCaja', id_trans, fecha_movimiento, importe, 1, vista, fecha_mod
    FROM t_trasladocaja WHERE id_trans = parm_trans;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_categorias_updatesubcategorias(IN p_id_categoria integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    -- Proceso que se usa en la edicion del articulo , cumple la funcion de editar los codigos de barra
	-- Teniendo encuenta los codigos nuevos , los codigos a elimnar y la actualizacion de datos para los codigos ya existentes

    -- 1. Eliminamos los códigos que ya no están en el modelo temporal
    DELETE FROM m_subcategorias t
    WHERE t.categoria_id = p_id_categoria
    AND NOT EXISTS (
        SELECT 1 FROM m_subcategoriasmodel m 
        WHERE m.categoria_id = p_id_categoria 
        AND m.id = t.id
    );
    
    -- 2. Actualizamos códigos existentes
    -- Nota: En el UPDATE de Postgres, la tabla destino no va en el FROM
    UPDATE m_subcategorias t
    SET 
        cod_subcategoria = m.cod_subcategoria,
        nom_subcategoria = m.nom_subcategoria
    FROM m_subcategoriasmodel m
    WHERE t.categoria_id = m.categoria_id
    AND t.id = m.id
    AND t.categoria_id = p_id_categoria;

    -- 3. Insertamos los registros nuevos
    -- Filtramos por id_codbarra = 0 (los que marcamos en FastAPI)
    INSERT INTO public.m_subcategorias (
        categoria_id, cod_subcategoria, nom_subcategoria
    )
    SELECT 
        m.categoria_id, m.cod_subcategoria, m.nom_subcategoria
    FROM m_subcategoriasmodel m
    WHERE m.categoria_id = p_id_categoria 
    AND m.id = 0
    AND NOT EXISTS (
        SELECT 1 FROM m_subcategorias t 
        WHERE t.categoria_id = categoria_id 
        AND t.id = m.id
    );

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_comercial_cierreturno(IN operacion character varying, IN parm_cierre integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_id_turno integer;
    v_id_caja integer;
    v_id_emp integer;
BEGIN
    SELECT tc.id_turno, ta.id_caja, tc.id_emp
    INTO v_id_turno, v_id_caja, v_id_emp
    FROM t_cierreturno tc
    JOIN t_abrirturno ta ON ta.id = tc.id_turno
    WHERE tc.id_trans = parm_cierre;

    IF v_id_turno IS NULL THEN
        RAISE EXCEPTION 'Cierre de turno % no encontrado', parm_cierre;
    END IF;

    INSERT INTO p_movimientocajas (
        id_trans, linea, id_emp, id_caja, id_mediopago, concepto,
        id_referencia, fec_doc, importe, signo, vista, fecha_mod
    )
    SELECT
        parm_cierre,
        ROW_NUMBER() OVER (ORDER BY tcd.id),
        v_id_emp,
        v_id_caja,
        tcd.id_mediopago,
        'CierreTurno',
        parm_cierre,
        CURRENT_DATE,
        tcd.valor_usuario,
        tcd.signo,
        'CierreTurno',
        now()
    FROM td_cierreturno tcd
    WHERE tcd.id_cierre = parm_cierre;

    UPDATE t_abrirturno SET status = false WHERE id = v_id_turno;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_comercial_movcaja(IN operacion character varying, IN parm_id integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_id_emp integer;
    v_id_efectivo integer;
BEGIN
    -- Resuelve la empresa via el turno -> caja del movimiento.
    SELECT c.id_emp INTO v_id_emp 
    FROM t_movcajas m
    JOIN t_abrirturno t ON t.id = m.id_turno
    JOIN m_cajas c ON c.id = t.id_caja
	JOIN m_conceptoscaja d ON m.id_concepto=d.id
    WHERE m.id = parm_id;


    -- Un movimiento de caja siempre es dinero fisico (efectivo) - no hay
    -- eleccion de medio de pago en el formulario.
    SELECT id INTO v_id_efectivo FROM m_mediopagos WHERE id_emp = v_id_emp AND tipo = 'Efectivo' LIMIT 1;

    -- Impacta el cuadre del turno igual que las facturas: una fila nueva en
    -- td_abrirturno, agrupada por separado de 'Factura' (concepto distinto
    -- segun el signo) para que se vea como una linea aparte en el cierre de
    -- turno. El importe se guarda YA con el signo aplicado (positivo para
    -- ingreso, negativo para gasto) para que la resta ya quede correcta en
    -- get_resumen_cierre/recalcularTotales sin tener que tocar esa logica.
    INSERT INTO public.td_abrirturno(
        id_turno, concepto, fecha, id_referencia, id_mediopago, importe, signo, vista)
    SELECT m.id_turno,
           CASE WHEN m.signo = 1 THEN 'IngresoCaja' ELSE 'GastoCaja' END,
           m.fecha_mod, m.id, v_id_efectivo, m.importe * m.signo, m.signo, 'MovCaja'
    FROM t_movcajas m
    WHERE m.id = parm_id;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_comercial_ventapos(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    -- Movimiento de caja/turno: si la venta tiene turno abierto, se registra en
    -- td_abrirturno (comportamiento igual a siempre). Si no tiene turno pero si
    -- tiene una caja elegida manualmente (venta-directa sin turno abierto), se
    -- registra en su lugar en p_movimientocajas, reusando el mismo id_trans de
    -- la venta. Ahora se genera UNA fila POR CADA linea de pago en
    -- td_facturas_mediopago (antes era una sola fila fija usando t_facturas.id_pago -
    -- soporta pago mixto, ej. Efectivo + Transferencia).
    INSERT INTO public.td_abrirturno(
        id_turno, concepto, fecha, id_referencia, id_mediopago, importe, signo, vista)
    SELECT f.id_turno, 'Factura', f.fecha_mod, f.id_trans, m.id_mediopago, m.importe, 1, f.vista
    FROM t_facturas f
    JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
    WHERE f.id_trans = parm_trans AND f.id_turno IS NOT NULL;

    INSERT INTO public.p_movimientocajas(
        id_trans, linea, id_emp, id_caja, id_mediopago, concepto, id_referencia, fec_doc, importe, signo, vista)
    SELECT f.id_trans, m.linea, f.id_emp, f.id_caja, m.id_mediopago, 'Factura', f.id_trans, f.fec_doc, m.importe, 1, f.vista
    FROM t_facturas f
    JOIN td_facturas_mediopago m ON m.id_emp = f.id_emp AND m.id_trans = f.id_trans
    WHERE f.id_trans = parm_trans AND f.id_turno IS NULL AND f.id_caja IS NOT NULL;

    delete from p_stock where id_trans=parm_trans;
    delete from p_costos where id_trans=parm_trans;

    insert into p_stock
    select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
    b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
    B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
    from t_facturas A
    inner join td_facturas B On a.id_trans=B.id_trans
    where A.id_trans=parm_trans;

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
	INSERT INTO public.m_artxcodigobarra(
	id_articulo, id_codbarra, cod_barra, ref_barra)
	select id_articulo, id_codbarra, cod_barra, ref_barra 
	FROM public.td_comprasnewcodbarra where id_trans=parm_trans;

	INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
	SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
	FROM public.td_comprasnuevolote WHERE id_trans=parm_trans;

	delete from p_stock where id_trans=parm_trans;
	delete from p_costos where id_trans=parm_trans;

	INSERT INTO public.p_costos(
	id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc, 
	id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo, 
	imp_costo_total, imp_costo_unitario, vista, fecha_mod)	
	select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
	b.id_articulo,b.cantidad,1 signo,
	COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
	B.costo_unit imp_costo_nuevo,
	0 imp_costo_adicional,
	COALESCE(D.cantidad, 0) stock_actual,
	(B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
	cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
	--(stock actual * costo actual)+ Costo total compra) / (stock actual + cantidad comprada)
	cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
	A.vista,A.fecha_mod
	from t_compras A
	inner join td_compras B On a.id_trans=B.id_trans
	inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
	left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
	where A.id_trans=parm_trans;

	insert into p_stock
	select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
	b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
	B.cantidad,1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
	from t_compras A
	inner join td_compras B On a.id_trans=B.id_trans
	inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
	where A.id_trans=parm_trans;

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_compras_devoluciones(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
	-- Idempotente: borra cualquier impacto previo de esta transaccion antes de re-insertar
	-- (permite reintentos y ediciones sin duplicar movimientos).
	DELETE FROM p_stock WHERE id_trans = parm_trans;
	DELETE FROM p_costos WHERE id_trans = parm_trans;

	-- Insertamos costos PRIMERO (antes de tocar p_stock): s_stkbodegas/s_costoxbodegas
	-- se recalculan a partir de p_stock (via trigger), asi que si insertaramos el
	-- stock antes, aqui ya leeriamos el saldo DESPUES del movimiento en vez de antes
	-- (mismo orden que ya usa sp_compradirecta, por la misma razon).
	-- Valorado al costo promedio ACTUAL de la bodega/articulo (sacar unidades no
	-- cambia el promedio de lo que queda, no se usa el costo historico de la compra
	-- origen). id_trans_ref/documento_ref/nro_docum_ref quedan apuntando a la compra origen.
	INSERT INTO p_costos(
	id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
	id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
	stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod)
	SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, A.id_compra_origen, A.documento, A.nro_docum,
	       C.documento, C.nro_docum, A.id_proveedor, A.fec_doc,
	       B.id_articulo, B.cantidad, -1 signo,
	       COALESCE(D.imp_costo_unitario, 0) imp_costo_actual,
	       COALESCE(D.imp_costo_unitario, 0) imp_costo_nuevo,
	       0 imp_costo_adicional,
	       COALESCE(E.cantidad, 0) stock_actual,
	       (COALESCE(E.cantidad, 0) - B.cantidad) stock_nuevo,
	       cast((COALESCE(D.imp_costo_unitario, 0) * B.cantidad) as numeric(20,2)) imp_costo_total,
	       COALESCE(D.imp_costo_unitario, 0) imp_costo_unitario,
	       A.vista, A.fecha_mod
	FROM t_devolucioncompras A
	INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
	INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
	LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
	LEFT JOIN s_stkbodegas E ON A.id_bodega = E.id_bodega AND B.id_articulo = E.id_articulo
	       AND A.id_estado = E.id_estado AND B.id_codbarra = E.id_codbarra
	WHERE A.id_trans = parm_trans;

	-- Insertamos Stock DESPUES: una devolucion siempre es una salida (signo -1).
	-- documento_ref/nro_ref quedan apuntando a la compra origen, para trazabilidad.
	INSERT INTO p_stock
	SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, C.documento, C.nro_docum, A.fec_doc,
	       B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, 0 id_ubicacion,
	       B.cantidad, -1 signo, null, A.vista, B.linea, 'Imp', A.fecha_mod
	FROM t_devolucioncompras A
	INNER JOIN td_devolucioncompras B ON A.id_trans = B.id_trans
	INNER JOIN t_compras C ON A.id_compra_origen = C.id_trans
	WHERE A.id_trans = parm_trans;

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_costeo_impacto_costeoxbodega(IN operacion character varying, IN parm_trans integer, IN parm_linea integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
	RAISE NOTICE 'linea: %', parm_linea;
    IF (operacion IN ('N')) THEN
        IF EXISTS (
            SELECT 1
            FROM p_costos A
            INNER JOIN s_costoxbodegas B
                ON  A.id_bodega = B.id_bodega
                AND A.id_articulo = B.id_articulo
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea
        ) THEN
            UPDATE s_costoxbodegas SET
				imp_costo_unitario=A.imp_costo_unitario,
                cantidad = A.stock_nuevo
            FROM p_costos A
            WHERE A.id_bodega = s_costoxbodegas.id_bodega
                AND A.id_articulo = s_costoxbodegas.id_articulo
                AND A.id_trans = parm_trans
                AND A.linea = parm_linea;
        ELSE
            INSERT INTO s_costoxbodegas (id_bodega,id_articulo,cantidad,imp_costo_unitario, proceso)
            SELECT
				A.id_bodega,
                A.id_articulo,
                A.stock_nuevo,
				A.imp_costo_unitario,
                A.vista
            FROM p_costos A
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea;
        END IF;
    ELSE -- Operacion Borrar: revertir por valor (cantidad*costo), no por snapshot.
         -- El termino que se resta/suma del pool de valor debe llevar el signo del
         -- movimiento que se esta revirtiendo: un signo=+1 (ej. compra) le resta valor
         -- al pool al revertirse; un signo=-1 (ej. devolucion) le SUMA valor de vuelta
         -- al pool al revertirse (antes esto siempre restaba, sin importar el signo,
         -- lo cual corrompia el costo promedio al revertir cualquier salida).
        UPDATE s_costoxbodegas SET
            cantidad = s_costoxbodegas.cantidad - (A.cantidad * A.signo),
            imp_costo_unitario = CASE
                WHEN (s_costoxbodegas.cantidad - (A.cantidad * A.signo)) <= 0 THEN s_costoxbodegas.imp_costo_unitario
                ELSE cast((((s_costoxbodegas.cantidad * s_costoxbodegas.imp_costo_unitario) - (A.imp_costo_total * A.signo)) / (s_costoxbodegas.cantidad - (A.cantidad * A.signo))) as numeric(20,2))
            END
        FROM p_costos A
        WHERE A.id_bodega = s_costoxbodegas.id_bodega
            AND A.id_articulo = s_costoxbodegas.id_articulo
            AND A.id_trans = parm_trans
            AND A.linea = parm_linea;
    END IF;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_general_control_stock(IN p_id_trans integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_existe_negativo boolean;
    v_articulo_err integer;
    v_bodega_err integer;
    v_saldo_err integer;	
BEGIN
    -- Validamos si alguna bodega quedó en negativo para esta transacción
   SELECT EXISTS (
        SELECT 1 
        FROM public.s_stkbodegas s
        INNER JOIN public.p_stock p 
            ON s.id_bodega = p.id_bodega
			AND s.id_estado = p.id_estado
			AND s.id_articulo = p.id_articulo             
            AND s.id_codbarra = p.id_codbarra           
        WHERE p.id_trans = p_id_trans
          AND s.cantidad < 0
    ) INTO v_existe_negativo;

   IF v_existe_negativo THEN
        -- Opcional: Capturamos los datos del primer artículo que falló para dar un mensaje detallado
        SELECT s.id_articulo, s.id_bodega, s.cantidad 
        INTO v_articulo_err, v_bodega_err, v_saldo_err
        FROM public.s_stkbodegas s
        INNER JOIN public.p_stock p 
             ON s.id_bodega = p.id_bodega
			AND s.id_estado = p.id_estado
			AND s.id_articulo = p.id_articulo             
            AND s.id_codbarra = p.id_codbarra      
        WHERE p.id_trans = p_id_trans AND s.cantidad < 0
        LIMIT 1;

        RAISE EXCEPTION 'ERR_VAL: El artículo ID % no tiene stock suficiente en la bodega ID %. Saldo restante: %', 
            v_articulo_err, v_bodega_err, v_saldo_err;
    END IF;
    
    -- Aquí puedes agregar más validaciones de stock...
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_general_control_transacciones(IN p_id_trans integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    -- Solo entra a validar stock si la transaccion realmente toco p_stock; evita
    -- perder tiempo validando cuando no aplica (ej. transacciones que no mueven stock),
    -- y deja el resto de este SP libre para agregar controles de otros modulos
    -- (cartera, etc.) sin que se validen entre si innecesariamente.
    IF EXISTS (SELECT 1 FROM public.p_stock WHERE id_trans = p_id_trans) THEN
        CALL sp_general_control_stock(p_id_trans);
    END IF;

    -- Puedes seguir anadiendo modulos aqui facilmente (sp_control_cartera, etc.)
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_ajustestock(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
	--Creamos los lotes nuevos (solo si la operacion es de creacion/finalizacion, igual que sp_compradirecta)
	INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
	SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
	FROM public.td_ajustestocknuevolote WHERE id_trans=parm_trans;

	--Borramos Stock
	delete from p_stock where id_trans=parm_trans;

	--Insertamos Stock
	insert into p_stock
	select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
	b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,B.id_ubicacion,
	B.cantidad,c.signo,null,A.vista,B.linea,'Imp',A.fecha_mod
	from t_ajustestock A
	inner join td_ajustestock B On a.id_trans=B.id_trans
	inner join m_motivoajuste C on A.id_motivo=C.id
	where A.id_trans=parm_trans;
		
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_cargastock(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
	-- Borramos impacto previo (permite reprocesar sin duplicar si algo se vuelve a llamar)
	DELETE FROM p_stock WHERE id_trans = parm_trans;
	DELETE FROM p_costos WHERE id_trans = parm_trans;

	-- Costos: el costo se toma directo del Excel (td_cargastock.costo), sin promediar
	-- contra el costo ya existente en la bodega (solo se deja como referencia informativa
	-- en imp_costo_actual/stock_actual, igual que compras).
	INSERT INTO p_costos (
		id_trans, linea, id_emp, id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref,
		id_proveedor, fec_doc, id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional,
		stock_actual, stock_nuevo, imp_costo_total, imp_costo_unitario, vista, fecha_mod
	)
	SELECT A.id_trans, B.linea, A.id_emp, A.id_bodega, 0, A.documento, A.nro_docum, NULL, NULL,
		A.id_proveedor, A.fecha_movimiento, B.id_articulo, B.cantidad, 1,
		COALESCE(D.imp_costo_unitario, 0),
		B.costo,
		0,
		COALESCE(D.cantidad, 0),
		(B.cantidad + COALESCE(D.cantidad, 0)),
		CAST((B.costo * B.cantidad) AS numeric(20,2)),
		CAST(B.costo AS numeric(20,2)),
		A.vista, A.fecha_mod
	FROM t_cargastock A
	INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
	LEFT JOIN s_costoxbodegas D ON A.id_bodega = D.id_bodega AND B.id_articulo = D.id_articulo
	WHERE A.id_trans = parm_trans;

	-- Stock
	INSERT INTO p_stock (
		id_trans, id_emp, documento, nro_docum, documento_ref, nro_ref, fec_doc,
		id_articulo, id_codbarra, id_bodega, id_estado, id_lote, id_ubicacion,
		cantidad, signo, fec_venc, vista, linea, serie, fecha_mod
	)
	SELECT A.id_trans, A.id_emp, A.documento, A.nro_docum, NULL, NULL, A.fecha_movimiento,
		B.id_articulo, B.id_codbarra, A.id_bodega, A.id_estado, B.id_lote, B.id_ubicacion,
		B.cantidad, 1, NULL, A.vista, B.linea, 'Imp', A.fecha_mod
	FROM t_cargastock A
	INNER JOIN td_cargastock B ON A.id_trans = B.id_trans
	WHERE A.id_trans = parm_trans;

END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_stkbodegas(IN operacion character varying, IN parm_trans integer, IN parm_linea integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
	RAISE NOTICE 'linea: %', parm_linea;
    IF (operacion IN ('N')) THEN
        IF EXISTS (
            SELECT 1
            FROM p_stock A
            INNER JOIN s_stkbodegas B
                ON  A.id_bodega = B.id_bodega
				AND A.id_estado = B.id_estado
                AND A.id_articulo = B.id_articulo
				AND A.id_codbarra=B.id_codbarra
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea
        ) THEN
            RAISE NOTICE 'Existe Articulo s_stkbodegas. Actualizando Stock.';
            UPDATE s_stkbodegas SET
                cantidad = s_stkbodegas.cantidad + (A.cantidad * A.signo)
            FROM p_stock A
            WHERE A.id_bodega = s_stkbodegas.id_bodega
				AND A.id_estado = s_stkbodegas.id_estado
                AND A.id_articulo = s_stkbodegas.id_articulo
				AND A.id_codbarra=s_stkbodegas.id_codbarra
                AND A.id_trans = parm_trans
                AND A.linea = parm_linea;
        ELSE
            RAISE NOTICE 'NO Existe Articulo s_stkbodegas. Creando nuevo registro de Stock.';
            INSERT INTO s_stkbodegas (id_bodega,id_estado, id_articulo,id_codbarra, cantidad, proceso, id_emp)
            SELECT
				A.id_bodega,
                A.id_estado,
                A.id_articulo,
				A.id_codbarra,
                (A.cantidad * A.signo),
                A.vista,
                A.id_emp
            FROM p_stock A
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea;
        END IF;
    ELSE
        RAISE NOTICE 'Operacion Borrar. Revertiendo Stock s_stkbodegas.';
        UPDATE s_stkbodegas SET
            cantidad = s_stkbodegas.cantidad - (A.cantidad * A.signo)
        FROM p_stock A
        WHERE A.id_bodega=s_stkbodegas.id_bodega
			AND A.id_estado = s_stkbodegas.id_estado
            AND A.id_articulo = s_stkbodegas.id_articulo
			AND A.id_codbarra=s_stkbodegas.id_codbarra
            AND A.id_trans = parm_trans
            AND A.linea = parm_linea;
    END IF;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_stkbodegaxlote(IN operacion character varying, IN parm_trans integer, IN parm_linea integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
    IF (operacion IN ('N')) THEN
        IF EXISTS (
            SELECT 1
            FROM p_stock A
            INNER JOIN s_stkbodegaxlote B
                ON  A.id_bodega = B.id_bodega
                AND A.id_estado = B.id_estado
                AND A.id_articulo = B.id_articulo
                AND A.id_lote = B.id_lote
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea
        ) THEN
            UPDATE s_stkbodegaxlote SET
                cantidad = s_stkbodegaxlote.cantidad + (A.cantidad * A.signo)
            FROM p_stock A
            WHERE A.id_bodega = s_stkbodegaxlote.id_bodega
                AND A.id_estado = s_stkbodegaxlote.id_estado
                AND A.id_articulo = s_stkbodegaxlote.id_articulo
                AND A.id_lote = s_stkbodegaxlote.id_lote
                AND A.id_trans = parm_trans
                AND A.linea = parm_linea;
        ELSE
            INSERT INTO s_stkbodegaxlote (id_bodega, id_estado, id_articulo, id_lote, cantidad, proceso, id_emp)
            SELECT
                A.id_bodega,
                A.id_estado,
                A.id_articulo,
                A.id_lote,
                (A.cantidad * A.signo),
                A.vista,
                A.id_emp
            FROM p_stock A
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea;
        END IF;
    ELSE
        UPDATE s_stkbodegaxlote SET
            cantidad = s_stkbodegaxlote.cantidad - (A.cantidad * A.signo)
        FROM p_stock A
        WHERE A.id_bodega = s_stkbodegaxlote.id_bodega
            AND A.id_estado = s_stkbodegaxlote.id_estado
            AND A.id_articulo = s_stkbodegaxlote.id_articulo
            AND A.id_lote = s_stkbodegaxlote.id_lote
            AND A.id_trans = parm_trans
            AND A.linea = parm_linea;
    END IF;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_stkestados(IN operacion character varying, IN parm_trans integer, IN parm_linea integer)
 LANGUAGE plpgsql
AS $procedure$

BEGIN
    IF (operacion IN ('N')) THEN
        IF EXISTS (
            SELECT 1
            FROM p_stock A
            JOIN s_stkestados B
                ON  A.id_estado = B.id_estado
                AND A.id_articulo = B.id_articulo
				AND A.id_codbarra=B.id_codbarra
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea
        ) THEN
            RAISE NOTICE 'Existe Articulo s_stkestados. Actualizando Stock.';
            UPDATE s_stkestados SET
                cantidad = s_stkestados.cantidad + (A.cantidad * A.signo)
            FROM p_stock A
            WHERE A.id_estado = s_stkestados.id_estado
                AND A.id_articulo = s_stkestados.id_articulo
				AND A.id_codbarra=s_stkestados.id_codbarra
                AND A.id_trans = parm_trans
                AND A.linea = parm_linea;
        ELSE
            RAISE NOTICE 'NO Existe Articulo s_stkestados. Creando nuevo registro de Stock.';
            INSERT INTO s_stkestados (id_estado, id_articulo,id_codbarra, cantidad, proceso, id_emp)
            SELECT
                A.id_estado,
                A.id_articulo,
				A.id_codbarra,
                (A.cantidad * A.signo),
                A.vista,
                A.id_emp
            FROM p_stock A
            WHERE A.id_trans = parm_trans
              AND A.linea = parm_linea;
        END IF;
    ELSE
        RAISE NOTICE 'Operacion Borrar. Revertiendo Stock s_stkestados.';
        UPDATE s_stkestados SET
            cantidad = s_stkestados.cantidad - (A.cantidad * A.signo)
        FROM p_stock A
        WHERE A.id_estado = s_stkestados.id_estado
            AND A.id_articulo = s_stkestados.id_articulo
			AND A.id_codbarra=s_stkestados.id_codbarra
            AND A.id_trans = parm_trans
            AND A.linea = parm_linea;
    END IF;
END;
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sp_stock_impacto_trasladobodega(IN operacion character varying, IN parm_trans integer)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
	--Borramos Stock
	delete from p_stock where id_trans=parm_trans;

    --primero baja de la bodega inicial
	insert into p_stock
	select A.id_trans,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
	b.id_articulo,b.id_codbarra,a.id_bodega_origen,a.id_estado_origen,B.id_lote,B.id_ubicacion,
	B.cantidad,-1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod
	from t_trasladobodega A
	inner join td_trasladobodega B On a.id_trans=B.id_trans
	where A.id_trans=parm_trans;

	--segundo sube a la bodega destino
	RAISE NOTICE 'Segundo impacto';
	insert into p_stock
	select A.id_trans,A.documento,a.nro_docum,null,null,A.fecha_movimiento,
	b.id_articulo,b.id_codbarra,a.id_bodega_destino,a.id_estado_destino,B.id_lote,B.id_ubicacion,
	B.cantidad,1 signo,null,A.vista,2 linea,'Imp2',A.fecha_mod
	from t_trasladobodega A
	inner join td_trasladobodega B On a.id_trans=B.id_trans
	where A.id_trans=parm_trans;

END;
$procedure$
;

CREATE OR REPLACE FUNCTION public.stockdisponiblexbodega(param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer, param_estado_id integer)
 RETURNS TABLE(stock integer)
 LANGUAGE plpgsql
AS $function$

DECLARE 
	v_stock integer;
BEGIN

	select cantidad from s_stkbodegas INTO v_stock
	where id_bodega=param_bodega_id
	and id_estado=param_estado_id
	and id_articulo=param_articulo_id
	and id_codbarra=param_id_codbarra;

	RETURN QUERY
	SELECT 
		COALESCE(v_stock, 0);
END
$function$
;

CREATE OR REPLACE FUNCTION public.ventadisponiblexbodega(param_articulo_id integer, param_id_codbarra integer, param_bodega_id integer, param_estado_id integer)
 RETURNS TABLE(stock integer, precio numeric, impuesto integer, porcentaje numeric)
 LANGUAGE plpgsql
AS $function$

DECLARE 
	v_stock integer;
	v_precio numeric(20,2);
	v_impuesto integer;
	v_porcentaje numeric;
BEGIN

	-- 3. Si por alguna razón el stock es NULL, se podría asignar 0 o un valor por defecto.
	-- Si quieres mantener la lógica de asignar 5 si es NULL, usa esto:
	
	select cantidad from s_stkbodegas INTO v_stock
	where id_bodega=param_bodega_id
	and id_estado=param_estado_id
	and id_articulo=param_articulo_id
	and id_codbarra=param_id_codbarra;

	select id_impuesto,B.porc_tasa from m_articulos A
	inner join m_impuesto B on A.id_impuesto=B.id
	INTO v_impuesto,v_porcentaje
	where id_articulo=param_articulo_id;
	
	-- Si solo quieres asegurar que es 0 si no se encuentra nada:
	-- v_stock := COALESCE(v_stock, 0);
	--select imp_costo_unitario  from s_costoxbodegas  INTO v_costo
	--where id_bodega=param_bodega_id
	--and id_articulo=param_articulo_id;

	v_precio := 200;
	
	RETURN QUERY
	SELECT 
		COALESCE(v_stock, 0),
		COALESCE(v_precio, 0),
		COALESCE(v_impuesto, 0),
		COALESCE(v_porcentaje, 0);
		
END
$function$
;

-- TRIGGERS
CREATE TRIGGER del_p_costos BEFORE DELETE ON public.p_costos FOR EACH ROW EXECUTE FUNCTION p_costos_delete();

CREATE TRIGGER ins_p_costos AFTER INSERT ON public.p_costos FOR EACH ROW EXECUTE FUNCTION p_costos_insert();

CREATE TRIGGER del_p_movimientocajas BEFORE DELETE ON public.p_movimientocajas FOR EACH ROW EXECUTE FUNCTION p_movimientocajas_delete();

CREATE TRIGGER ins_p_movimientocajas AFTER INSERT ON public.p_movimientocajas FOR EACH ROW EXECUTE FUNCTION p_movimientocajas_insert();

CREATE TRIGGER del_p_stock BEFORE DELETE ON public.p_stock FOR EACH ROW EXECUTE FUNCTION p_stock_delete();

CREATE TRIGGER ins_p_stock AFTER INSERT ON public.p_stock FOR EACH ROW EXECUTE FUNCTION p_stock_insert();
