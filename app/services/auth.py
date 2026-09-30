from app.repositories.contracts import UsuariosRepository
from app.schemas.auth import Registro
from app.utils.errors import DomainError, Unauthorized
from app.utils.security import TokenManager, hash_password, verify_password


class AuthService:
    def __init__(self, repository: UsuariosRepository, tokens: TokenManager):
        self.repository = repository
        self.tokens = tokens

    def register(self, data: Registro):
        email = str(data.email).lower()
        if self.repository.by_email(email):
            raise DomainError('El email ya está registrado', 'email_duplicado', 409)
        return self.repository.add(email, hash_password(data.password))

    def login(self, email: str, password: str) -> str:
        user = self.repository.by_email(email.strip().lower())
        if user is None or not verify_password(password, user.password_hash):
            raise Unauthorized()
        return self.tokens.issue(user.id)

    def authenticate(self, token: str):
        claims = self.tokens.decode(token)
        user = self.repository.by_id(int(claims['sub']))
        if user is None:
            raise Unauthorized()
        return user
