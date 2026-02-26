from fastapi import FastAPI
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
from app.modules.core.empresas.controller_empresa import router as empresas
from app.modules.core.negocios.controller_negocio import router as negocios
from app.modules.impuestos.impuesto.controller_impuesto import router as impuestos
from app.core.Services.ServiceInicializacion.controller_serviciosIni import router as serviciosini
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(title="Mi ERP API")

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