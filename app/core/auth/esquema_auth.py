from pydantic import BaseModel

# Lo que envía Angular
class LoginRequest(BaseModel):
    usuario: str
    clave: str

# Los datos estáticos del usuario que Angular guardará en memoria
class UsuarioFrenter(BaseModel):
    idUsuario : int
    usuario: str
    nombre: str

# Los datos de la empresa
class EmpresaFrenter(BaseModel):
    idEmp : int
    nomEmpresa: str    

# Lo que responde FastAPI con éxito
class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UsuarioFrenter
    empresa : EmpresaFrenter