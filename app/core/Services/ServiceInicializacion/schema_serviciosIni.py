

from decimal import Decimal

from pydantic import BaseModel

class NumeradorResponse(BaseModel):
    next_value: int

# Esquema Compra Disponible
class StockDisponibleResponse(BaseModel):
    stock: int
    costo: Decimal
 