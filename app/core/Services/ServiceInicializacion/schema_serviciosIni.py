

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

class NumeradorResponse(BaseModel):
    next_value: int

# Esquema Compra Disponible
class StockDisponibleCompraResponse(BaseModel):
    stock: int
    costo: Decimal
    impuesto: int
    porcentaje: Decimal
    # % de utilidad (markup) sugerido para este articulo, resuelto por la
    # jerarquia subcategoria -> categoria -> general dentro de la propia
    # funcion SQL comprasdisponiblexbodega. None = nada configurado en ningun
    # nivel (no sugiere, no es lo mismo que 0%).
    porc_utilidad: Optional[Decimal] = None

# Esquema venta Disponible
class StockDisponibleResponse(BaseModel):
    stock: int
    precio: Decimal
    impuesto : int
    porcentaje : Decimal
 