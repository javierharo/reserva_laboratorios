from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Registro(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator('password')
    @classmethod
    def bcrypt_length(cls, value: str) -> str:
        if len(value.encode('utf-8')) > 72:
            raise ValueError('La contraseña no puede superar 72 bytes UTF-8')
        return value


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'
