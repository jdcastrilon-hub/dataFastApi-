from fastapi import HTTPException

"""
Chequeo generico de "configuracion de modulo requerida", para usar en los
endpoints que dependen de un valor definido en una tabla m_conf<modulo>
(m_confcompras, m_confcomercial, y las que se agreguen a futuro para otros
modulos como Bodega/Stock). Mismo espiritu que verificar_permiso en
app/core/auth/permisos.py: una funcion de una linea al tope del save/edit,
deny by default - si la empresa no configuro el valor todavia, se corta la
operacion con un mensaje amigable en vez de asumir un default "sensato" o
dejar que la BD reviente mas abajo con un error generico.

Este helper NO sabe nada de que tabla o modulo se trata - cada modulo sigue
dueno de su propia tabla m_conf<modulo> y su propio repository_confxxx.py
(get_confxxx(db, id_emp)); aca solo se centraliza el "cortar con un 400 y
un mensaje claro" para que sea igual en todos.

Ejemplo (Compra Directa, ver controller_compras.py):
    conf = repository_confcompras.get_confcompras(db, contexto.id_emp)
    compra.id_estado = requerir_configurado(
        conf.id_estado_comp if conf else None,
        "Falta configurar el estado de mercancía por defecto en "
        "Compras > Configuración antes de registrar una compra."
    )
"""


def requerir_configurado(valor, mensaje: str):
    if valor is None:
        raise HTTPException(status_code=400, detail=mensaje)
    return valor
