from typing import Annotated

from fastapi import APIRouter, Header, Query, Response

from app.routers.dependencies import ReservaDep, UserDep
from app.schemas.reservas import PreparacionOut, ReservaIn, ReservaOut
from app.services.reservas import LABORATORIOS

router = APIRouter(tags=['Reservas'])


@router.get('/laboratorios/')
def labs(user: UserDep):
    return [{'id': key, 'nombre': value} for key, value in LABORATORIOS.items()]


@router.post('/reservas/', response_model=ReservaOut, status_code=201)
def create(data: ReservaIn, user: UserDep, service: ReservaDep):
    return service.create(user.id, data)


@router.get('/reservas/', response_model=list[ReservaOut])
def list_reservas(user: UserDep, service: ReservaDep,
                  skip: Annotated[int, Query(ge=0)] = 0,
                  limit: Annotated[int, Query(ge=1, le=100)] = 20):
    return service.list(user.id, skip, limit)


@router.get('/reservas/{reserva_id}', response_model=ReservaOut)
def get(reserva_id: int, user: UserDep, service: ReservaDep):
    return service.get(user.id, reserva_id)


@router.put('/reservas/{reserva_id}', response_model=ReservaOut)
def update(reserva_id: int, data: ReservaIn, user: UserDep, service: ReservaDep):
    return service.update(user.id, reserva_id, data)


@router.post('/reservas/{reserva_id}/preparar-cancelacion', response_model=PreparacionOut)
def prepare_cancel(reserva_id: int, user: UserDep, service: ReservaDep):
    return service.prepare_cancel(user.id, reserva_id)


@router.delete('/reservas/{reserva_id}', status_code=204)
def cancel(reserva_id: int, user: UserDep, service: ReservaDep,
           confirmacion: Annotated[str, Header(alias='X-Confirmacion')] = '',
           confirmar: bool = False):
    service.cancel(user.id, reserva_id, confirmacion, confirmar)
    return Response(status_code=204)
