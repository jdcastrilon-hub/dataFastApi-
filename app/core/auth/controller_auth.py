from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth.esquema_auth import (
    LoginRequest,
    LoginResponse,
    EmpresaFrenter,
    CambiarEmpresaRequest,
    CambiarEmpresaResponse,
    EmpresaPrincipalRequest,
    EmpresaMiaFrenter,
)
from app.core.auth.security import verificar_password, crear_token_acceso, obtener_contexto_actual, ContextoUsuario
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

    empresas_usuario_query = (
        db.query(model_empresa.Empresa)
        .join(model_empresa.EmpresaXUser, model_empresa.Empresa.id_emp == model_empresa.EmpresaXUser.id_emp)
        .filter(
            model_empresa.EmpresaXUser.id_usuario == usuario_db.id_usuario,
            model_empresa.EmpresaXUser.activo == True,
            model_empresa.Empresa.activa == True,
        )
    )

    # Preferimos la empresa marcada como principal (ver model_usuario.py); si no
    # hay una marcada, o el usuario ya no tiene acceso activo a ella, cae al
    # comportamiento anterior (la primera empresa activa que aparezca).
    empresa_activa = None
    if usuario_db.id_emp_principal:
        empresa_activa = empresas_usuario_query.filter(
            model_empresa.Empresa.id_emp == usuario_db.id_emp_principal
        ).first()
    if not empresa_activa:
        empresa_activa = empresas_usuario_query.first()

    if not empresa_activa:
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

    # 4. Generar el Token de acceso firmando el usuario y la empresa activa
    token = crear_token_acceso(subject=usuario_db.id_usuario, id_emp=empresa_activa.id_emp)

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
            "idEmp":empresa_activa.id_emp,
            "nomEmpresa":empresa_activa.nom_emp
        }
    }


@router.get("/mis-empresas", response_model=List[EmpresaMiaFrenter])
def mis_empresas(contexto: ContextoUsuario = Depends(obtener_contexto_actual), db: Session = Depends(get_db)):
    """Empresas activas a las que el usuario autenticado tiene acceso, para el selector de cambio de empresa."""
    empresas = (
        db.query(model_empresa.Empresa)
        .join(model_empresa.EmpresaXUser, model_empresa.Empresa.id_emp == model_empresa.EmpresaXUser.id_emp)
        .filter(
            model_empresa.EmpresaXUser.id_usuario == contexto.usuario.id_usuario,
            model_empresa.EmpresaXUser.activo == True,
            model_empresa.Empresa.activa == True,
        )
        .all()
    )
    return [
        {
            "idEmp": e.id_emp,
            "nomEmpresa": e.nom_emp,
            "esPrincipal": e.id_emp == contexto.usuario.id_emp_principal,
        }
        for e in empresas
    ]


@router.post("/cambiar-empresa", response_model=CambiarEmpresaResponse)
def cambiar_empresa(
    datos: CambiarEmpresaRequest,
    contexto: ContextoUsuario = Depends(obtener_contexto_actual),
    db: Session = Depends(get_db),
):
    """Emite un token nuevo firmado con la empresa destino, revalidando en este
    instante que el usuario sigue teniendo acceso activo a ella."""
    empresa_destino = (
        db.query(model_empresa.Empresa)
        .join(model_empresa.EmpresaXUser, model_empresa.Empresa.id_emp == model_empresa.EmpresaXUser.id_emp)
        .filter(
            model_empresa.EmpresaXUser.id_usuario == contexto.usuario.id_usuario,
            model_empresa.EmpresaXUser.id_emp == datos.idEmp,
            model_empresa.EmpresaXUser.activo == True,
            model_empresa.Empresa.activa == True,
        )
        .first()
    )

    if not empresa_destino:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a la empresa solicitada",
        )

    token = crear_token_acceso(subject=contexto.usuario.id_usuario, id_emp=empresa_destino.id_emp)

    return {
        "token": token,
        "token_type": "bearer",
        "empresa": {
            "idEmp": empresa_destino.id_emp,
            "nomEmpresa": empresa_destino.nom_emp,
        },
    }


@router.put("/empresa-principal")
def marcar_empresa_principal(
    datos: EmpresaPrincipalRequest,
    contexto: ContextoUsuario = Depends(obtener_contexto_actual),
    db: Session = Depends(get_db),
):
    """Marca la empresa indicada como la que el login del usuario usara por
    defecto (ver model_usuario.py::id_emp_principal). Valida que siga teniendo
    acceso activo a ella, mismo criterio que cambiar-empresa - no se puede
    marcar como principal una empresa a la que no pertenece."""
    tiene_acceso = (
        db.query(model_empresa.EmpresaXUser)
        .join(model_empresa.Empresa, model_empresa.Empresa.id_emp == model_empresa.EmpresaXUser.id_emp)
        .filter(
            model_empresa.EmpresaXUser.id_usuario == contexto.usuario.id_usuario,
            model_empresa.EmpresaXUser.id_emp == datos.idEmp,
            model_empresa.EmpresaXUser.activo == True,
            model_empresa.Empresa.activa == True,
        )
        .first()
    )
    if not tiene_acceso:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a la empresa solicitada",
        )

    contexto.usuario.id_emp_principal = datos.idEmp
    db.commit()

    return {
        "status": "success",
        "message": "Empresa principal actualizada",
        "data": None
    }