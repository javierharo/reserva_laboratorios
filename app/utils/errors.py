class DomainError(Exception):
    def __init__(self, message: str, code: str = 'regla_invalida', status: int = 400):
        super().__init__(message)
        self.code = code
        self.status = status


class NotFound(DomainError):
    def __init__(self):
        super().__init__('Reserva no encontrada', 'no_encontrada', 404)


class Unauthorized(DomainError):
    def __init__(self):
        super().__init__('Credenciales o token inválidos', 'no_autorizado', 401)
