from sqlalchemy import desc
from sqlalchemy.orm import Session ,joinedload 
from . import model_negocios
from app.modules.stock.categorias import models
from app.modules.stock.tiposervicio import model_servicio

# Obtener todas las bodegas ordenadas de mayor a menor
def get_negocios(db: Session):
    return db.query(model_negocios.Negocio).all()

def get_negocios_con_categorias_por_empresa(db: Session, id_empresa: int):
        # 1. Obtenemos todos los negocios de la empresa
        negocios = db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id_emp == id_empresa).all()

        # 2. Obtenemos todas las categorías de la empresa con sus subcategorías
        categorias = db.query(models.Categoria).filter(models.Categoria.id_emp == id_empresa).options(
                                    joinedload(models.Categoria.subcategorias)).all()
        
        tipoproducto = db.query(model_servicio.TipoServicio).filter(model_servicio.TipoServicio.id_emp == id_empresa).all()

        # 3. Mapeamos la lista de objetos Negocio al formato del DTO
        # Inyectamos la lista de categorías en cada negocio
        return {
                "idEmpresa": id_empresa,
                "nombreEmpresa": "juan",
                "listnegocio": negocios,
                "listCategorias":categorias,
                "tipoproductos":tipoproducto
        }
        