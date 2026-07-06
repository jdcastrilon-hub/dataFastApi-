from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth.esquema_auth import LoginRequest, LoginResponse
from app.core.auth.security import verificar_password, crear_token_acceso
from app.modules.core.usuarios import model_usuario
from app.modules.core.empresas import model_empresa
from app.database import get_db


router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    # 1. Buscar el usuario en la base de datos de Postgres
    usuario_db = db.query(model_usuario.Usuario).filter(model_usuario.Usuario.usuario == datos.usuario).first()
    
    # 2. Si no existe, lanzamos error genérico (por seguridad no decimos cuál falló)
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )
    
    empresas_usuario = (
        db.query(model_empresa.Empresa)
        .join(model_empresa.EmpresaXUser, model_empresa.Empresa.id_emp == model_empresa.EmpresaXUser.id_emp)
        .filter(model_empresa.EmpresaXUser.id_usuario == usuario_db.id_usuario)
        .first()
        )
    
    if not empresas_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene asociada una empresa"
        )
        
    # 3. Validar la contraseña
    if not verificar_password(datos.clave, usuario_db.clave):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )
        
    # 4. Generar el Token de acceso usando el ID del usuario
    token = crear_token_acceso(subject=usuario_db.id_usuario)
    
    # 5. Retornar la respuesta estructurada acorde a nuestro esquema
    return {
        "token": token,
        "token_type": "bearer",
        "user": {
            "idUsuario" : usuario_db.id_usuario,
            "usuario": usuario_db.usuario,
            "nombre": usuario_db.nom_usuario
        },
        "empresa":{
            "idEmp":empresas_usuario.id_emp,
            "nomEmpresa":empresas_usuario.nom_emp
        }
    }