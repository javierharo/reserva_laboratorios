from datetime import datetime, timedelta, timezone
import secrets

import jwt
import pytest
from pydantic import ValidationError

from app.schemas.auth import Registro
from app.services.auth import AuthService
from app.utils.config import Settings
from app.utils.errors import DomainError, Unauthorized
from app.utils.security import AUDIENCE, ISSUER, verify_password
from tests.fakes import FakeUsuarios


@pytest.fixture
def service(tokens):
    return AuthService(FakeUsuarios(), tokens)


def test_R7_email_duplicado(service):
    user = service.register(Registro(email='Mateo@example.com', password='Prueba-123'))
    assert user.email == 'mateo@example.com'
    assert user.password_hash != 'Prueba-123'
    assert verify_password('Prueba-123', user.password_hash)
    with pytest.raises(DomainError) as exc:
        service.register(Registro(email='MATEO@example.com', password='Otra-123'))
    assert exc.value.code == 'email_duplicado'


def test_R8_login(service):
    user = service.register(Registro(email='uno@example.com', password='Prueba-123'))
    token = service.login(' UNO@example.com ', 'Prueba-123')
    assert service.authenticate(token).id == user.id
    for email, password in [('uno@example.com', 'incorrecta'), ('dos@example.com', 'Prueba-123'),
                             ('uno@example.com', 'x' * 73)]:
        with pytest.raises(Unauthorized):
            service.login(email, password)
    with pytest.raises(Unauthorized):
        service.authenticate(service.tokens.issue(999))


def test_R8_tokens(tokens):
    for invalid in ('basura', tokens.issue(1, purpose='cancel')):
        with pytest.raises(Unauthorized):
            tokens.decode(invalid)
    now = datetime.now(timezone.utc)
    claims = {'sub': '1', 'purpose': 'access', 'iat': now - timedelta(hours=1),
              'exp': now - timedelta(minutes=1), 'iss': ISSUER, 'aud': AUDIENCE}
    expired = jwt.encode(claims, tokens.settings.jwt_secret.get_secret_value(), algorithm='HS256')
    with pytest.raises(Unauthorized):
        tokens.decode(expired)
    forged = jwt.encode({**claims, 'exp': now + timedelta(minutes=5)},
                        secrets.token_urlsafe(48), algorithm='HS256')
    with pytest.raises(Unauthorized):
        tokens.decode(forged)
    claims['purpose'] = 'cancel'
    with pytest.raises(DomainError, match='vencida'):
        tokens.decode(jwt.encode(claims, tokens.settings.jwt_secret.get_secret_value(),
                                 algorithm='HS256'), purpose='cancel')


def test_settings_y_password(settings):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret='corta')
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret=settings.jwt_secret, database_url='postgresql://db')
    with pytest.raises(ValidationError):
        Registro(email='uno@example.com', password='á' * 40)
