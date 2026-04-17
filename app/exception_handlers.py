from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError, IntegrityError

def add_exception_handlers(app):
    
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
    # 2. Error de Integridad de Base de Datos (PK duplicada, FK, etc.)
    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        msg = str(exc.orig)
        
        # Valores por defecto
        status_code = status.HTTP_400_BAD_REQUEST
        friendly_msg = "No se pudo completar la operación debido a una restricción en la base de datos."
        error_detail = "Integrity violation"

        # Caso A: Violación de Llave Foránea (Delete/Update)
        if "is still referenced from table" in msg or "viola la llave foránea" in msg:
            friendly_msg = "No se puede eliminar este registro porque tiene información relacionada con otro modulo."
            error_detail = "ForeignKeyViolation"

        # Caso B: Registro Duplicado (Unique Constraint)
        elif "already exists" in msg or "ya existe" in msg:
            friendly_msg = "No se puede guardar: Ya existe un registro con estos datos únicos."
            error_detail = "UniqueViolation"
            
        # Caso C: Valor nulo en campo requerido
        elif "null value in column" in msg:
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