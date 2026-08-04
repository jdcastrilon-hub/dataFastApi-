import re

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError, IntegrityError, InternalError

from app.exceptions import TransaccionValidationError

# Centraliza la limpieza del mensaje 'ERR_VAL: ...' que usan los RAISE EXCEPTION
# de los SPs/triggers de control de negocio (ver sp_general_control_stock y
# cualquier trigger de limite de plan) - una sola vez para todo el ERP, sin
# importar si llega envuelto en TransaccionValidationError (repository con
# try/except propio, ej. ventas/compras) o crudo como InternalError (INSERT
# normal sin try/except, ej. un trigger BEFORE INSERT en bodegas).
def _limpiar_mensaje_err_val(mensaje_completo: str) -> str:
    if "ERR_VAL:" not in mensaje_completo:
        return "La transacción fue rechazada por controles internos."
    try:
        return re.search(r"ERR_VAL:\s*(.*?)(?=\n|$)", mensaje_completo).group(1)
    except AttributeError:
        return mensaje_completo.split("ERR_VAL:")[1].split("\n")[0].strip()

def add_exception_handlers(app, allowed_origin_pattern=None):
    origen_permitido_re = re.compile(allowed_origin_pattern) if allowed_origin_pattern else None

    def _cors_headers(request: Request) -> dict:
        # El handler de Exception corre en ServerErrorMiddleware, que en Starlette
        # queda POR FUERA del CORSMiddleware del usuario (este solo envuelve
        # ExceptionMiddleware hacia adentro). Por eso las respuestas de los demás
        # handlers sí llevan headers CORS automáticamente, pero esta no — hay que
        # agregarlos a mano, reflejando el mismo origen permitido que CORSMiddleware,
        # o el navegador descarta la respuesta como si fuera un fallo de CORS.
        origin = request.headers.get("origin")
        if origin and origen_permitido_re and origen_permitido_re.match(origin):
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
            }
        return {}

    # 1. Error de validación de Pydantic (Datos mal formados)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error1",
                "message": "Los datos enviados son incorrectos o están incompletos.",
                "data": exc.errors()
            },
        )

    # 2. Error de Integridad de Base de Datos (PK duplicada, FK, etc.)
    #
    # Se detecta por el código SQLSTATE que Postgres siempre entrega (independiente
    # del idioma del servidor), en vez de buscar frases dentro del mensaje de error:
    # el texto puede venir en inglés o español según la configuración de Postgres,
    # y buscar "ya existe"/"viola la llave foránea" fallaba en silencio, cayendo
    # siempre al mensaje genérico.
    SQLSTATE_UNIQUE_VIOLATION = "23505"
    SQLSTATE_FOREIGN_KEY_VIOLATION = "23503"
    SQLSTATE_NOT_NULL_VIOLATION = "23502"

    # Mensajes puntuales por nombre de constraint, para cuando el genérico ("Ya
    # existe un registro con ese código...") no le dice al usuario CUÁL valor está
    # duplicado. Postgres siempre entrega el nombre de la constraint en el error
    # (exc.orig.diag.constraint_name), así que no hace falta adivinar por texto.
    # Cualquier constraint no listada aquí sigue usando el mensaje genérico.
    MENSAJES_UNIQUE_VIOLATION = {
        "t_compras_unique": "Ya existe una compra registrada con ese número de remito para este proveedor.",
        "ux_listaprecio_general_por_emp": "Ya existe una lista de precios general activa para esta empresa. Solo puede haber una.",
        "ux_bodega_principal_por_sucursal": "Ya existe una bodega principal activa para esta sucursal. Desactive o quite el estado de principal a la actual antes de asignar otra.",
    }

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        pgcode = getattr(exc.orig, "pgcode", None)
        diag = getattr(exc.orig, "diag", None)
        columna = getattr(diag, "column_name", None) if diag else None
        constraint = getattr(diag, "constraint_name", None) if diag else None

        # Valores por defecto
        status_code = status.HTTP_400_BAD_REQUEST
        friendly_msg = "No se pudo completar la operación debido a una restricción en la base de datos."
        error_detail = "Integrity violation"

        # En un DELETE, cualquier violación de integridad significa lo mismo para
        # el usuario: el registro sigue en uso en otro módulo. Esto cubre también
        # el caso en que la FK tiene ON DELETE SET NULL pero la columna referenciada
        # es NOT NULL: ahí Postgres reporta un NotNullViolation (23502), no un
        # ForeignKeyViolation (23503), aunque la causa real sea la misma.
        if request.method == "DELETE":
            friendly_msg = "No se puede eliminar este registro porque tiene información relacionada con otro modulo."
            error_detail = "ForeignKeyViolation"

        elif pgcode == SQLSTATE_UNIQUE_VIOLATION:
            friendly_msg = MENSAJES_UNIQUE_VIOLATION.get(
                constraint,
                "Ya existe un registro con ese código o valor único. Verifica los datos e intenta nuevamente."
            )
            error_detail = "UniqueViolation"

        elif pgcode == SQLSTATE_FOREIGN_KEY_VIOLATION:
            friendly_msg = "No se puede eliminar este registro porque tiene información relacionada con otro modulo."
            error_detail = "ForeignKeyViolation"

        elif pgcode == SQLSTATE_NOT_NULL_VIOLATION:
            friendly_msg = f"El campo '{columna}' es obligatorio." if columna else "Error: Un campo obligatorio está vacío."
            error_detail = "NotNullViolation"

        else:
            # Respaldo por si el driver no expone pgcode: se busca el texto en
            # minúsculas y cubriendo variantes en inglés y español.
            msg = str(exc.orig).lower()
            if "is still referenced from table" in msg or "viola la llave foránea" in msg or "violates foreign key" in msg:
                friendly_msg = "No se puede eliminar este registro porque tiene información relacionada con otro modulo."
                error_detail = "ForeignKeyViolation"
            elif "already exists" in msg or "ya existe" in msg or "duplicate key" in msg or "llave duplicada" in msg:
                friendly_msg = "Ya existe un registro con ese código o valor único. Verifica los datos e intenta nuevamente."
                error_detail = "UniqueViolation"
            elif "null value in column" in msg or "viola la restricción de no nulo" in msg:
                friendly_msg = "Error: Un campo obligatorio está vacío."
                error_detail = "NotNullViolation"

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": friendly_msg,
                "data": {
                    "code": error_detail,
                    # En producción podrías ocultar 'msg' y solo dejarlo en logs
                    "detail": "Restricción de integridad en la base de datos."
                }
            },
    )

    # 3. Error genérico (Cualquier cosa que se rompa)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error3",
                "message": "Ha ocurrido un error inesperado en el servidor.",
                "data": str(exc)
            },
            headers=_cors_headers(request),
        )
    
    @app.exception_handler(DataError)
    async def sqlalchemy_data_error_handler(request: Request, exc: DataError):
        # Extraemos el mensaje amigable de psycopg2
        # El error original está en exc.orig
        error_msg = str(exc.orig).split('\n')[0] 
        
        # Personalizamos el mensaje para el usuario
        mensaje_amigable = "Error de formato: Uno de los campos excede la longitud permitida o tiene un tipo incorrecto."
        
        return JSONResponse(
            status_code=400,
            content={
                "status": "error4",
                "message": mensaje_amigable,
                "data": error_msg # Enviamos el detalle técnico para depurar en desarrollo
            }
        )


    @app.exception_handler(TransaccionValidationError)
    async def validation_error_handler(request: Request, exc: TransaccionValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": _limpiar_mensaje_err_val(exc.message),
                "data": None # Enviamos el detalle técnico para depurar en desarrollo
            }
        )

    # 4. RAISE EXCEPTION crudo de un trigger (sin pasar por un try/except propio del
    # repository, ej. un BEFORE INSERT que valida un limite de plan). SQLAlchemy lo
    # entrega como InternalError con pgcode P0001, no como IntegrityError/DataError.
    # Solo se traduce a mensaje amigable si trae el prefijo 'ERR_VAL:' (control de
    # negocio conocido) - cualquier otro InternalError sigue siendo un 500 real,
    # no se lo tragamos en silencio.
    @app.exception_handler(InternalError)
    async def internal_error_handler(request: Request, exc: InternalError):
        mensaje_original = str(getattr(exc, "orig", exc))

        if "ERR_VAL:" in mensaje_original:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": _limpiar_mensaje_err_val(mensaje_original),
                    "data": None
                }
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error3",
                "message": "Ha ocurrido un error inesperado en el servidor.",
                "data": mensaje_original
            },
            headers=_cors_headers(request),
        )