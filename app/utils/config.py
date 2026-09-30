from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    jwt_secret: SecretStr
    database_url: str = 'sqlite:///./reservas.db'
    access_token_minutes: int = Field(default=30, ge=1, le=1440)
    confirmation_seconds: int = Field(default=120, ge=1, le=600)

    @field_validator('jwt_secret')
    @classmethod
    def strong_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError('JWT_SECRET debe tener al menos 32 caracteres aleatorios')
        return value

    @field_validator('database_url')
    @classmethod
    def sqlite_only(cls, value: str) -> str:
        if not value.startswith('sqlite:///'):
            raise ValueError('Este MVP utiliza SQLite; configura sqlite:///ruta.db')
        return value
