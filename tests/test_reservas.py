from datetime import date

import pytest

from app.schemas.reservas import ReservaIn
from app.services.reservas import ReservaService
from app.utils.errors import DomainError, NotFound
from tests.fakes import FakeReservas

DAY = date(2030, 1, 10)


def data(**changes):
    return ReservaIn(**{'laboratorio_id': 1, 'fecha': DAY, 'hora_inicio': '09:00',
                        'hora_fin': '10:00', 'motivo': 'Práctica de redes', **changes})


@pytest.fixture
def service(tokens):
    return ReservaService(FakeReservas(), tokens, today=lambda: DAY)


@pytest.mark.parametrize('fin', ['08:00', '09:00'])
def test_R1_horario_invalido(service, fin):
    with pytest.raises(DomainError, match='posterior'):
        service.create(1, data(hora_fin=fin))
    assert service.list(1) == []


@pytest.mark.parametrize('inicio,fin', [('09:00', '10:00'), ('08:30', '09:30'),
                                         ('09:30', '11:00'), ('08:00', '11:00'),
                                         ('09:10', '09:50')])
def test_R2_solapamiento(service, inicio, fin):
    service.create(1, data())
    with pytest.raises(DomainError) as exc:
        service.create(2, data(hora_inicio=inicio, hora_fin=fin))
    assert exc.value.code == 'solapamiento'
    assert len(service.list(1)) == 1
    assert service.list(2) == []


def test_R2_adyacentes_y_otro_laboratorio(service):
    service.create(1, data())
    service.create(2, data(hora_inicio='10:00', hora_fin='11:00'))
    service.create(2, data(hora_inicio='08:00', hora_fin='09:00'))
    service.create(2, data(laboratorio_id=2))
    service.create(2, data(fecha=date(2030, 1, 11)))
    assert len(service.list(2)) == 4


def test_R2_actualizacion(service):
    first = service.create(1, data())
    second = service.create(2, data(hora_inicio='11:00', hora_fin='12:00'))
    assert service.update(1, first.id, data(motivo='Otro motivo')).version == 2
    with pytest.raises(DomainError, match='reservado'):
        service.update(2, second.id, data())
    assert service.get(2, second.id).hora_inicio.hour == 11


def test_R3_aislamiento(service):
    row = service.create(1, data())
    assert service.list(2) == []
    assert service.get(1, row.id).usuario_id == 1
    for action in (lambda: service.get(2, row.id),
                   lambda: service.update(2, row.id, data()),
                   lambda: service.prepare_cancel(2, row.id),
                   lambda: service.get(1, 999)):
        with pytest.raises(NotFound):
            action()
    own_confirmation = service.tokens.issue(2, purpose='cancel', reserva_id=row.id, version=1)
    with pytest.raises(NotFound):
        service.cancel(2, row.id, own_confirmation, True)
    assert len(service.list(1)) == 1


def test_R4_fecha_pasada(service):
    with pytest.raises(DomainError, match='anterior'):
        service.create(1, data(fecha=date(2030, 1, 9)))
    assert service.create(1, data()).fecha == DAY


def test_R5_laboratorio(service):
    with pytest.raises(DomainError, match='no existe'):
        service.create(1, data(laboratorio_id=99))


def test_R6_confirmacion(service):
    row = service.create(1, data())
    prep = service.prepare_cancel(1, row.id)
    assert prep.reserva.id == row.id
    with pytest.raises(DomainError, match='explícitamente'):
        service.cancel(1, row.id, prep.confirmacion, False)
    with pytest.raises(DomainError, match='inválida'):
        service.cancel(1, row.id, 'inventado', True)
    with pytest.raises(DomainError, match='inválida'):
        service.cancel(1, row.id, service.tokens.issue(1), True)
    wrong_user = service.tokens.issue(2, purpose='cancel', reserva_id=row.id, version=1)
    wrong_id = service.tokens.issue(1, purpose='cancel', reserva_id=999, version=1)
    for token in (wrong_user, wrong_id):
        with pytest.raises(DomainError, match='no corresponde'):
            service.cancel(1, row.id, token, True)
    service.update(1, row.id, data())
    with pytest.raises(DomainError, match='vigente'):
        service.cancel(1, row.id, prep.confirmacion, True)
    service.cancel(1, row.id, service.prepare_cancel(1, row.id).confirmacion, True)
    with pytest.raises(NotFound):
        service.cancel(1, row.id, prep.confirmacion, True)


@pytest.mark.parametrize('skip,limit', [(-1, 20), (0, 0), (0, 101)])
def test_paginacion(service, skip, limit):
    with pytest.raises(DomainError, match='Paginación'):
        service.list(1, skip, limit)
