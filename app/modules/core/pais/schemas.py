from pydantic import BaseModel

# Lo que el cliente envía al crear (sin el ID)
class PaisCreate(BaseModel):
    cod_pais: str
    nom_pais: str

# Lo que la API responde (con el ID)
class PaisResponse(BaseModel):
    id_pais: int
    cod_pais: str
    nom_pais: str
