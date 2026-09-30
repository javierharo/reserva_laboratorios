from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.repositories.sqlalchemy import SQLReservasRepository, SQLUsuariosRepository
from app.services.auth import AuthService
from app.services.reservas import ReservaService

oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/token')


def get_session(request: Request):
    with request.app.state.sessions() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_auth_service(request: Request, session: SessionDep):
    return AuthService(SQLUsuariosRepository(session), request.app.state.tokens)


def get_reserva_service(request: Request, session: SessionDep):
    return ReservaService(SQLReservasRepository(session), request.app.state.tokens)


def get_current_user(token: Annotated[str, Depends(oauth2)],
                     service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.authenticate(token)


AuthDep = Annotated[AuthService, Depends(get_auth_service)]
ReservaDep = Annotated[ReservaService, Depends(get_reserva_service)]
UserDep = Annotated[object, Depends(get_current_user)]
