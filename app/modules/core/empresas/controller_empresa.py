from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_empresa, schema_empresa
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos) - solo Ver+Editar (no
# es un CRUD, es un registro unico por empresa)
MENU_CODIGO = "ADM_EMP"

router = APIRouter(
    prefix="/core/empresas",
    tags=["Core - Empresas"])

@router.get("/list", response_model=List[schema_empresa.EmpresaListaCombo])
def listar_empresas( db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresas(db)

@router.get("/listByNegocios", response_model=List[schema_empresa.EmpresaListaByNegocios])
def listar_empresas( db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las empresas."""
    return repository_empresa.get_empresasByNegocios(db)

@router.get("/mi-empresa", response_model=schema_empresa.EmpresaPerfilResponse)
def obtener_mi_empresa(id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Datos de perfil de la empresa activa (pantalla 'Mi Empresa' en Administracion)."""
    db_empresa = repository_empresa.get_empresa(db, id_emp=id_emp)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.put("/mi-empresa")
def actualizar_mi_empresa(id_emp: int, empresa: schema_empresa.EmpresaPerfilUpdate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita el perfil de la empresa activa (ver nota en otros modulos sobre el manejo de errores: sin try/except local, lo resuelve el manejador global)."""
    verificar_permiso(db, usuario_autenticado.id_usuario, id_emp, MENU_CODIGO, "EDITAR")
    db_empresa = repository_empresa.update_empresa_perfil(db, id_emp=id_emp, obj=empresa)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return {
        "status": "success",
        "message": "Empresa actualizada exitosamente",
        "data": None
    }

@router.post("/save", dependencies=[Depends(security.verificar_clave_admin_interna)])
def crear_empresa(empresa: schema_empresa.EmpresaCreate, db: Session = Depends(get_db)):
    """Provisioning interno: crea una empresa nueva con su rol superadmin, asocia
    un usuario YA EXISTENTE, y carga los 4 maestros base con valores fijos via
    sp_core_nuevaempresa - todo en una transaccion. No usa el flujo JWT normal
    (ver security.verificar_clave_admin_interna, la misma clave interna que ya
    usa POST /core/menu/agregar) porque la empresa/usuario-en-esa-empresa no
    existen todavia al momento de la llamada. Sin try/except local, ver nota en
    otros modulos sobre el manejo de errores."""
    bd_empresa = repository_empresa.create_empresa(db=db, obj=empresa)
    return {
        "status": "success",
        "message": "Empresa creada exitosamente",
        "data": {"idEmp": bd_empresa.id_emp}
    }