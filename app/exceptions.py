
class TransaccionValidationError(Exception):
    """
    Excepción personalizada para capturar errores de validación 
    lanzados por los procedimientos almacenados (SPs) en la base de datos.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)