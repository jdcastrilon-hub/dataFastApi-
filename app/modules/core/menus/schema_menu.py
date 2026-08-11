from pydantic import BaseModel, Field
from typing import List, Optional

ACCIONES_POR_DEFECTO = ['VER', 'CREAR', 'EDITAR', 'BUSCAR', 'ELIMINAR']

# Body de POST /core/menu/agregar - mismo shape que scripts/agregar_formulario_menu.py,
# ahora expuesto como endpoint (protegido: solo el usuario de plataforma, ver
# controller_menu.py). Registra md_menu + md_menu_permisos en una transaccion.
class AgregarFormularioRequest(BaseModel):
    codigo: str = Field(..., description="Codigo unico del menu, ej. INV_LOTES")
    nombre: str = Field(..., description="Nombre a mostrar")
    id_modulo: int = Field(..., alias="idModulo")
    id_padre: Optional[int] = Field(None, alias="idPadre", description="id_menu del contenedor padre (omitir si es raiz)")
    # Si el formulario tiene lista + formulario (new/edit) separados, esto DEBE
    # ser la ruta de la LISTA (ej. "/categorias"), nunca "/categoria/new" - el
    # sidebar navega directo a este valor (menu-item-component.component.html),
    # y "/new" suele estar guardado con permisoGuard exigiendo CREAR. Un
    # usuario con solo VER (sin CREAR) quedaria bloqueado en /no-autorizado al
    # hacer click, aunque el permiso este bien otorgado (bug real, corregido
    # 2026-08-04 en INV_CAT/INV_BOD/INV_ART/INV_TRAS/INV_AJU/INV_CARGA).
    ruta: str = Field(..., description="Ruta Angular de la LISTA (o pseudo-ruta si visible=false) - no la de /new")
    icono: Optional[str] = Field(None, description="Nombre del icono Material (opcional)")
    orden: int = Field(99, description="Orden dentro de su nivel")
    visible: bool = Field(True, description="False para formularios que no deben aparecer como item propio en el sidebar")
    acciones: List[str] = Field(default_factory=lambda: list(ACCIONES_POR_DEFECTO),
                                 description="Codigos de md_permisos a habilitar para este formulario")

    class Config:
        populate_by_name = True


class MenuResponse(BaseModel):
    id_menu: int
    codigo: str
    nombre: str
    ruta: Optional[str] = None
    icono: Optional[str] = None
    es_contenedor: bool

    children: List["MenuResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


MenuResponse.model_rebuild()