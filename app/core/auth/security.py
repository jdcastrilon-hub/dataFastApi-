import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Union
import jwt
from jwt.exceptions import InvalidTokenError  # <-- Esta es la clase que te hace falta
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.modules.core.usuarios import model_usuario

load_dotenv()

# Configuración del encriptador de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CONFIGURACIÓN DEL JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta la variable de entorno SECRET_KEY (ver .env)")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Horas de jornada laboral

# Esto le dice a FastAPI que busque el token en la cabecera "Authorization: Bearer <TOKEN>"
# El tokenUrl apunta al endpoint donde se hace el login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="core/usuarios/login")

# Clave interna fija para endpoints de uso exclusivo por Postman (mantenimiento
# de plataforma: agregar formularios al menu, creacion de empresas, etc.) - no
# requieren sesion de usuario ni JWT, no se llaman desde el frontend. Una sola
# clave compartida entre todos esos endpoints (no una por endpoint), asi el
# environment de Postman solo necesita una entrada. Hardcodeada aqui (no en
# .env) - es el mismo criterio que ya traia este secreto desde antes, movida
# de controller_menu.py sin cambiar su valor.
CLAVE_ADMIN_INTERNA = "ZQv6Ae_b97ZNmZKU7uh0nBsC5dQypIXZy84SV_j9Xy8"

def verificar_clave_admin_interna(x_admin_key: str = Header(...)):
    if x_admin_key != CLAVE_ADMIN_INTERNA:
        raise HTTPException(status_code=403, detail="Clave de administracion invalida")

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la clave que ingresa el usuario con la encriptada en la BD"""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password: str) -> str:
    """Genera un hash seguro para guardar en la BD al crear usuarios"""
    # Forzamos a string plano de Python para evitar cualquier desborde de búfer de bytes de la librería
    password_puro = str(password)
    return pwd_context.hash(password_puro)

def crear_token_acceso(subject: Union[str, Any], id_emp: int) -> str:
    """Genera el token JWT con un tiempo de expiración, firmando la empresa activa"""
    tiempo_expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "exp": tiempo_expiracion,
        "sub": str(subject),  # Identificador del usuario (id_usuario)
        "idEmp": id_emp,  # Empresa activa de la sesión, validada al momento de firmar
    }

    token_encriptado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_encriptado

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de acceso no válidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # PyJWT valida la expiración (exp) internamente al decodificar
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        
        if usuario_id is None:
            raise credentials_exception
            
    except InvalidTokenError:
        # Si se cumplen las 8 horas o el token es inválido, saltará aquí directamente
        raise credentials_exception

    # Buscamos el usuario en la base de datos para asegurarnos de que sigue activo
    usuario = db.query(model_usuario.Usuario).filter(model_usuario.Usuario.id_usuario == int(usuario_id)).first()

    if usuario is None or not usuario.activo:
        raise credentials_exception

    return usuario # Retornamos el objeto usuario completo de la BD


@dataclass
class ContextoUsuario:
    """Usuario autenticado + empresa activa, ambos derivados del JWT firmado."""
    usuario: model_usuario.Usuario
    id_emp: int


def obtener_contexto_actual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> ContextoUsuario:
    """Igual que obtener_usuario_actual, pero además exige y devuelve el idEmp
    firmado en el token. Pensada para el endpoint de cambiar-empresa y para
    que los controladores de negocio la adopten progresivamente en vez de
    recibir id_emp como parámetro de request."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de acceso no válidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        id_emp = payload.get("idEmp")

        if usuario_id is None or id_emp is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    usuario = db.query(model_usuario.Usuario).filter(model_usuario.Usuario.id_usuario == int(usuario_id)).first()

    if usuario is None or not usuario.activo:
        raise credentials_exception

    return ContextoUsuario(usuario=usuario, id_emp=id_emp)