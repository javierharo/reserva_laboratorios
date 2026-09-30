from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.routers.dependencies import AuthDep
from app.schemas.auth import Registro, TokenOut, UsuarioOut

router = APIRouter(prefix='/auth', tags=['Autenticación'])


@router.post('/registro', response_model=UsuarioOut, status_code=201)
def register(data: Registro, service: AuthDep):
    return service.register(data)


@router.post('/token', response_model=TokenOut)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthDep):
    return TokenOut(access_token=service.login(form.username, form.password))
