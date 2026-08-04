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

# Item del selector de "Cambiar empresa" (mis-empresas): igual que EmpresaFrenter
# mas la marca de cual es la empresa principal actual del usuario.
class EmpresaMiaFrenter(EmpresaFrenter):
    esPrincipal: bool

# Lo que responde FastAPI con éxito
class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UsuarioFrenter
    empresa : EmpresaFrenter

# Lo que envía Angular al cambiar de empresa activa
class CambiarEmpresaRequest(BaseModel):
    idEmp: int

# Lo que responde FastAPI al cambiar de empresa (token nuevo firmado con la empresa elegida)
class CambiarEmpresaResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    empresa: EmpresaFrenter

# Lo que envía Angular al marcar una empresa como la principal (la que el login
# usa por defecto). Independiente de cambiar-empresa: no requiere estar
# activo en esa empresa en este momento para marcarla.
class EmpresaPrincipalRequest(BaseModel):
    idEmp: int