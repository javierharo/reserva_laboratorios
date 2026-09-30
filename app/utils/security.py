from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.utils.config import Settings
from app.utils.errors import DomainError, Unauthorized

ISSUER = 'reservas-laboratorios'
AUDIENCE = 'reservas-api-mcp'


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('ascii')


def verify_password(password: str, hashed: str) -> bool:
    if len(password.encode('utf-8')) > 72:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('ascii'))


class TokenManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    def issue(self, usuario_id: int, purpose: str = 'access', **claims) -> str:
        seconds = (self.settings.access_token_minutes * 60 if purpose == 'access'
                   else self.settings.confirmation_seconds)
        now = datetime.now(timezone.utc)
        payload = {**claims, 'sub': str(usuario_id), 'purpose': purpose,
                   'iat': now, 'exp': now + timedelta(seconds=seconds),
                   'iss': ISSUER, 'aud': AUDIENCE}
        return jwt.encode(payload, self.settings.jwt_secret.get_secret_value(), algorithm='HS256')

    def decode(self, token: str, purpose: str = 'access') -> dict:
        try:
            claims = jwt.decode(token, self.settings.jwt_secret.get_secret_value(),
                                algorithms=['HS256'], issuer=ISSUER, audience=AUDIENCE,
                                options={'require': ['sub', 'exp', 'iat', 'purpose']})
            if claims['purpose'] != purpose or not claims['sub'].isdigit():
                raise ValueError('Tipo o sujeto inválido')
            return claims
        except (jwt.InvalidTokenError, ValueError, KeyError, AttributeError) as exc:
            if purpose == 'access':
                raise Unauthorized() from exc
            raise DomainError('Confirmación inválida o vencida', 'confirmacion_invalida') from exc
