from fastapi import FastAPI, Request , status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.exception_handlers import add_exception_handlers
from app.modules.core.pais.controller import router as pais_router
from app.modules.stock.bodegas.controller_bodega import router as bodegas
from app.modules.core.sucursales.controller_sucursal import router as sucursales
from app.modules.stock.categorias.controller_categoria import router as categorias
from app.modules.stock.articulos.controller_articulos import router as articulos
from app.modules.stock.unidades.controller_unidad import router as unidades
from app.modules.stock.costeo.controller_costeo import router as costeo
from app.modules.stock.motivosStock.controller_motivoajuste import router as motivos
from app.modules.stock.ajusteStock.controller_ajusteStock import router as ajustestock
from app.modules.stock.estados.controller_estado import router as estados
from app.modules.stock.trasladostock.controller_trasladoStock import router as traslado
from app.modules.stock.cargastock.controller_cargastock import router as cargastock
from app.modules.stock.tiposervicio.controller_servicios import router as tiposervicio
from app.modules.stock.monitorstock.controller_monitor import router as monitorstock
from app.modules.core.empresas.controller_empresa import router as empresas
from app.modules.core.negocios.controller_negocio import router as negocios
from app.modules.core.ciudades.controller_ciudades import router as ciudad
from app.modules.core.menus.controller_menu import router as menus
from app.modules.core.usuarios.controller_usuario import router as usuarios
from app.modules.core.roles.controller_rol import router as roles
from app.modules.core.permisos.controller_permiso import router as permisos
from app.modules.impuestos.impuesto.controller_impuesto import router as impuestos
from app.modules.compras.documentos.controller_documentos import router as tipodoc
from app.modules.compras.personas.controller_personas import router as persona
from app.modules.compras.proveedores.controller_proveedor import router as provedor
from app.modules.compras.compradirecta.controller_compras import router as compra
from app.modules.compras.monitorcompras.controller_monitor import router as monitorcompras
from app.modules.compras.ajustecostos.controller_ajustecosto import router as ajusteCostos
from app.modules.compras.motivosdevolucion.controller_motivodevolucion import router as motivosdevolucion
from app.modules.compras.devolucioncompras.controller_devolucion import router as devolucioncompras
from app.modules.comercial.clientes.controller_cliente import router as cliente
from app.modules.comercial.ventas.controller_ventas import router as ventas
from app.modules.comercial.mediopago.controller_medio import router as mediopagos
from app.modules.comercial.cajas.controller_cajas import router as cajas
from app.modules.comercial.listaprecio.controller_listaprecio import router as listaprecio
from app.modules.comercial.ajusteprecio.controller_ajusteprecio import router as ajusteprecio
from app.modules.comercial.cargaprecios.controller_cargaprecios import router as cargaprecios
from app.modules.comercial.turnos.controller_turno import router as turno
from app.modules.comercial.cierreturno.controller_cierreturno import router as cierreturno
from app.modules.comercial.movimientocaja.controller_movcaja import router as movimientocaja
from app.modules.comercial.documentos.controller_docum import router as documventas
from app.modules.comercial.monitoroperaciones.controller_monitor import router as monitoroperaciones
from app.modules.tesoreria.conceptos.controller_conceptos import router as conceptos
from app.core.numeradores.controller_numerador import router as numeradores
from app.core.Services.ServiceInicializacion.controller_serviciosIni import router as serviciosini
from app.core.auth.controller_auth import router as inicioSesion
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(title="Mi ERP API")

# Origen(es) de entrada permitidos: localhost, o cualquier IP de red privada
# (192.168.x.x / 10.x.x.x / 172.16-31.x.x) en el puerto 4200 - permite acceder
# desde otro PC de la misma red local sin tener que hardcodear una IP puntual
# que cambia con el DHCP.
ORIGIN_PATTERN = r"^http://(localhost|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):4200$"

# exeptiones del sistema
add_exception_handlers(app, allowed_origin_pattern=ORIGIN_PATTERN)

# Registrar los módulos (Como si fueran Controllers en Spring)
#app.include_router(stock_router)
#app.include_router(compras_router)

@app.get("/")
def health_check():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ORIGIN_PATTERN,
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Permite todos los headers
)

app.include_router(pais_router)
app.include_router(bodegas)
app.include_router(sucursales)
app.include_router(categorias)
app.include_router(empresas)
app.include_router(negocios)
app.include_router(articulos)
app.include_router(unidades)
app.include_router(costeo)
app.include_router(impuestos)
app.include_router(serviciosini)
app.include_router(motivos)
app.include_router(estados)
app.include_router(ajustestock)
app.include_router(tipodoc)
app.include_router(persona)
app.include_router(ciudad)
app.include_router(provedor)
app.include_router(compra)
app.include_router(traslado)
app.include_router(cargastock)
app.include_router(monitorcompras)
app.include_router(tiposervicio)
app.include_router(monitorstock)
app.include_router(ajusteCostos)
app.include_router(motivosdevolucion)
app.include_router(devolucioncompras)
app.include_router(cliente)
app.include_router(ventas)
app.include_router(mediopagos)
app.include_router(cajas)
app.include_router(listaprecio)
app.include_router(ajusteprecio)
app.include_router(cargaprecios)
app.include_router(turno)
app.include_router(cierreturno)
app.include_router(movimientocaja)
app.include_router(documventas)
app.include_router(monitoroperaciones)
app.include_router(conceptos)
app.include_router(numeradores)
app.include_router(menus)
app.include_router(usuarios)
app.include_router(roles)
app.include_router(permisos)
app.include_router(inicioSesion)