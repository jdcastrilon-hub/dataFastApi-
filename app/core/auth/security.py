from datetime import datetime, timedelta
from typing import Any, Union
import jwt  
from jwt.exceptions import InvalidTokenError  # <-- Esta es la clase que te hace falta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.modules.core.usuarios import model_usuario 

# Configuración del encriptador de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CONFIGURACIÓN DEL JWT (Idealmente estas variables van en tu archivo .env)
SECRET_KEY = "TU_LLAVE_SECRETA_SUPER_SEGURA_Y_LARGA" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Horas de jornada laboral

# Esto le dice a FastAPI que busque el token en la cabecera "Authorization: Bearer <TOKEN>"
# El tokenUrl apunta al endpoint donde se hace el login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="core/usuarios/login")

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la clave que ingresa el usuario con la encriptada en la BD"""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password: str) -> str:
    """Genera un hash seguro para guardar en la BD al crear usuarios"""
    return pwd_context.hash(password)

def crear_token_acceso(subject: Union[str, Any]) -> str:
    """Genera el token JWT con un tiempo de expiración"""
    tiempo_expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "exp": tiempo_expiracion,
        "sub": str(subject)  # Aquí guardamos el identificador del usuario (ej. id o usuario)
    }
    
    token_encriptado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_encriptado


def obtener_password_hash(password: str) -> str:
    # Forzamos a string plano de Python para evitar cualquier desborde de búfer de bytes de la librería
    password_puro = str(password)
    return pwd_context.hash(password_puro)

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