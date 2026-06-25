from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import datetime

class MedioPagoCombo(BaseModel):
    id: int = Field(alias="id")
    tipo: str = Field(alias="tipo", max_length=20)

    model_config = ConfigDict(
    from_attributes=True,  
    populate_by_name=True)