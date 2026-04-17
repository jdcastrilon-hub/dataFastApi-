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
from app.modules.stock.reporteInventario.controller_reporteinventario import router as reporteinventario
from app.modules.stock.tiposervicio.controller_servicios import router as tiposervicio
from app.modules.stock.monitorstock.controller_monitor import router as monitorstock
from app.modules.core.empresas.controller_empresa import router as empresas
from app.modules.core.negocios.controller_negocio import router as negocios
from app.modules.core.ciudades.controller_ciudades import router as ciudad
from app.modules.impuestos.impuesto.controller_impuesto import router as impuestos
from app.modules.compras.documentos.controller_documentos import router as tipodoc
from app.modules.compras.personas.controller_personas import router as persona
from app.modules.compras.proveedores.controller_proveedor import router as provedor
from app.modules.compras.compradirecta.controller_compras import router as compra
from app.modules.compras.monitorcompras.controller_monitor import router as monitorcompras
from app.core.Services.ServiceInicializacion.controller_serviciosIni import router as serviciosini
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(title="Mi ERP API")

# exeptiones del sistema
add_exception_handlers(app)

# Registrar los módulos (Como si fueran Controllers en Spring)
#app.include_router(stock_router)
#app.include_router(compras_router)

@app.get("/")
def health_check():
    return {"status": "ok"}

#URL de entrada permitida
origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
app.include_router(reporteinventario)
app.include_router(monitorcompras)
app.include_router(tiposervicio)
app.include_router(monitorstock)