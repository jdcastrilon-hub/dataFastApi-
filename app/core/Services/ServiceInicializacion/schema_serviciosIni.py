from pydantic import BaseModel

class NumeradorResponse(BaseModel):
    next_value: int