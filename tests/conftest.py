import secrets

import pytest

from app.utils.config import Settings
from app.utils.security import TokenManager


@pytest.fixture
def settings(tmp_path):
    return Settings(_env_file=None, jwt_secret=secrets.token_urlsafe(48),
                    database_url=f'sqlite:///{tmp_path / "test.db"}')


@pytest.fixture
def tokens(settings):
    return TokenManager(settings)
