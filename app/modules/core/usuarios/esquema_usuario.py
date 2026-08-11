from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from app.modules.compras.personas import schema_personas

#Esquema para leer la varaiable Logs
class LogEntry(BaseModel):
    operacion: str
    usuario_mod: str
    fecha_mod: str

class UsuarioBase(BaseModel):
    id_emp: int = Field(alias="idEmp")
    id_usuario: Optional[int] = Field(None, alias="idUsuario")
    id_persona: Optional[int] = Field(None, alias="idPersona")
    usuario: str = Field(alias="usuario", max_length=20)
    # Opcional: en edicion, en blanco significa "no cambiar la clave actual".
    clave: Optional[str] = Field(None, alias="clave", max_length=100)
    nom_usuario: str = Field(alias="nomUsuario", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry]
    # Se reutiliza PersonaDetalle (no PersonaBase): sus alias ya coinciden con el
    # payload real que arma PersonaComponent.aPayload() en el frontend (codigoTitular,
    # fechaNacimiento, email, etc.) - PersonaBase usa un juego de alias distinto
    # (codTit, fecNacimiento, sin alias en mail/sexo) pensado para otro caso de uso.
    persona: Optional[schema_personas.PersonaDetalle] = None
    # Aprovecha el alta/edicion del usuario para asignarlo de una vez a sus
    # tablas base (en vez de crearlo y despues ir a Roles/Sucursales por
    # separado). idRol es unico (no lista): un usuario solo puede tener un rol
    # no-superadmin por empresa (ver repository_rol.py::_validar_un_rol_por_usuario,
    # misma regla aplicada del otro lado en la grilla de usuarios del rol) -
    # None/omitido significa "sin rol asignado todavia". Sucursales si es lista,
    # ahi no aplica la misma restriccion. El repository valida que cada id
    # pertenezca a id_emp antes de insertar (defensivo, mismo criterio que
    # guardar_matriz).
    id_rol: Optional[int] = Field(default=None, alias="idRol")
    sucursales: List[int] = Field(default=[], alias="sucursales")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class UsuarioCreate(UsuarioBase):
    pass

# Esquema para la respuesta (lo que devuelve /search por id, usado en ver/editar)
class UsuarioResponse(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    id_persona: int = Field(alias="idPersona")
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nomUsuario", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry]
    persona: schema_personas.PersonaDetalle
    # Rol/sucursales actualmente asignados (para pre-seleccionar los pickers
    # al editar) - solo los ids, el picker ya trae el combo completo.
    id_rol: Optional[int] = Field(default=None, alias="idRol")
    sucursales: List[int] = Field(default=[], alias="sucursales")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

# Esquema usado por el autocompletar (combo-usuario, asignacion de cajas/conceptos, etc.)
class UsuarioSearch(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nombreCompleto", max_length=100)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Esquema para paginacion (lista de la pestaña Usuarios de Administracion)
class UsuarioPaginacion(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nomUsuario", max_length=100)
    activo: bool = Field(alias="activo")
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)

class PaginatedUsuarioResponse(BaseModel):
    content: List[UsuarioPaginacion]
    totalElements: int
    totalPages: int
    number: int
    size: int

# "Mi Perfil" (modal en el toolbar): datos propios del usuario logueado, con los
# roles que tiene en la empresa activa (solo informativo - no editables desde aca).
class MiPerfilRol(BaseModel):
    id_rol: int = Field(alias="idRol")
    nombre: str = Field(alias="nombre")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MiPerfilResponse(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nomUsuario", max_length=100)
    persona: schema_personas.PersonaDetalle
    roles: List[MiPerfilRol] = Field(default=[])
    # Se devuelve para que el frontend la reenvie intacta en el PUT (el update
    # reemplaza el jsonb completo) - sin esto, cada auto-edicion borraria el
    # historial de auditoria previo del usuario.
    logs: List[LogEntry] = Field(default=[])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Edicion propia: solo usuario/nomUsuario/persona. Sin activo (lo maneja
# Administracion > Usuarios) ni clave (cambio de clave queda para una etapa
# posterior, ver conversacion con el cliente).
class MiPerfilUpdate(BaseModel):
    usuario: str = Field(alias="usuario", max_length=20)
    nom_usuario: str = Field(alias="nomUsuario", max_length=100)
    fecha_mod: Optional[datetime] = Field(None, alias="fechaMod")
    logs: List[LogEntry]
    persona: schema_personas.PersonaDetalle

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
