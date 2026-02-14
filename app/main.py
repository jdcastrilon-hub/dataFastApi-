from fastapi import FastAPI
from app.modules.core.pais.controller import router as pais_router
from app.modules.stock.bodegas.controller_bodega import router as bodegas
from app.modules.core.sucursales.controller_sucursal import router as sucursales
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
