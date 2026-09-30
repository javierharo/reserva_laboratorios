from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import threading

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from app.main import create_app
from app.models.entities import Usuario
from app.repositories.sqlalchemy import SQLReservasRepository, SQLUsuariosRepository
from app.schemas.reservas import ReservaIn
from app.services.reservas import ReservaService, today_ecuador
from app.utils.errors import DomainError


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


def register_login(client, email):
    result = client.post('/auth/registro', json={'email': email, 'password': 'Demo-12345'})
    assert result.status_code == 201
    assert 'password_hash' not in result.json()
    token = client.post('/auth/token', data={'username': email, 'password': 'Demo-12345'})
    assert token.status_code == 200
    return {'Authorization': 'Bearer ' + token.json()['access_token']}


def payload(**changes):
    return {'laboratorio_id': 1, 'fecha': (today_ecuador() + timedelta(days=1)).isoformat(),
            'hora_inicio': '09:00', 'hora_fin': '10:00', 'motivo': 'Práctica', **changes}


def test_rest_crud_y_aislamiento(client, app):
    alice = register_login(client, 'alice@example.com')
    bob = register_login(client, 'bob@example.com')
    assert client.get('/health').status_code == 200
    assert len(client.get('/laboratorios/', headers=alice).json()) == 3
    created = client.post('/reservas/', headers=alice, json=payload())
    assert created.status_code == 201
    row_id = created.json()['id']
    assert client.get(f'/reservas/{row_id}', headers=alice).json()['usuario_id'] == 1
    assert len(client.get('/reservas/', headers=alice).json()) == 1
    assert client.get('/reservas/', headers=bob).json() == []
    assert client.get(f'/reservas/{row_id}', headers=bob).status_code == 404
    assert client.put(f'/reservas/{row_id}', headers=bob, json=payload()).status_code == 404
    assert client.post('/reservas/', headers=bob, json=payload()).status_code == 409
    update = client.put(f'/reservas/{row_id}', headers=alice, json=payload(motivo='Actualizado'))
    assert update.status_code == 200 and update.json()['version'] == 2
    assert client.delete(f'/reservas/{row_id}', headers=alice).status_code == 400
    prep = client.post(f'/reservas/{row_id}/preparar-cancelacion', headers=alice).json()
    cancel_headers = {**alice, 'X-Confirmacion': prep['confirmacion']}
    assert client.delete(f'/reservas/{row_id}?confirmar=true', headers=cancel_headers).status_code == 204
    assert client.get(f'/reservas/{row_id}', headers=alice).status_code == 404
    with app.state.sessions() as session:
        user = session.scalar(select(Usuario).where(Usuario.email == 'alice@example.com'))
        assert user.password_hash.startswith('$2b$')


def test_auth_todas_las_rutas(client):
    for method, url, body in [('GET', '/laboratorios/', None), ('GET', '/reservas/', None),
                               ('GET', '/reservas/1', None), ('POST', '/reservas/', payload()),
                               ('PUT', '/reservas/1', payload()), ('DELETE', '/reservas/1', None),
                               ('POST', '/reservas/1/preparar-cancelacion', None)]:
        assert client.request(method, url, json=body).status_code == 401
    assert client.get('/reservas/', headers={'Authorization': 'Bearer invalido'}).status_code == 401
    assert client.post('/auth/token', data={'username': 'nadie@example.com',
                                           'password': 'invalida'}).status_code == 401
    assert client.post('/mcp/', json={}).status_code == 401


def test_rest_errores_y_formatos(client):
    headers = register_login(client, 'validar@example.com')
    assert client.post('/auth/registro', json={'email': 'VALIDAR@example.com',
                                               'password': 'Otra-12345'}).status_code == 409
    assert client.post('/reservas/', headers=headers,
                       json=payload(usuario_id=999)).status_code == 422
    assert client.post('/reservas/', headers=headers,
                       json=payload(hora_inicio='invalida')).status_code == 422
    assert client.post('/reservas/', headers=headers,
                       json=payload(hora_inicio='09:00+02:00')).status_code == 422
    assert client.post('/reservas/', headers=headers,
                       json=payload(motivo='  ')).status_code == 422
    assert client.post('/reservas/', headers=headers,
                       json=payload(hora_fin='08:00')).status_code == 400
    assert client.get('/reservas/?limit=101', headers=headers).status_code == 422
    assert client.post('/reservas/999/preparar-cancelacion', headers=headers).status_code == 404


def test_repositorio_email_unico(app):
    with app.state.sessions() as session:
        repo = SQLUsuariosRepository(session)
        repo.add('unique@example.com', 'hash-de-prueba')
        with pytest.raises(DomainError) as exc:
            repo.add('unique@example.com', 'otro-hash')
        assert exc.value.code == 'email_duplicado'


def test_cancelacion_no_reutiliza_id(client):
    headers = register_login(client, 'replay@example.com')
    first = client.post('/reservas/', headers=headers, json=payload()).json()
    prep = client.post(f'/reservas/{first["id"]}/preparar-cancelacion', headers=headers).json()
    cancellation = {**headers, 'X-Confirmacion': prep['confirmacion']}
    assert client.delete(f'/reservas/{first["id"]}?confirmar=true',
                         headers=cancellation).status_code == 204
    second = client.post('/reservas/', headers=headers, json=payload()).json()
    assert second['id'] > first['id']
    assert client.delete(f'/reservas/{second["id"]}?confirmar=true',
                         headers=cancellation).status_code == 400
    assert client.get(f'/reservas/{second["id"]}', headers=headers).status_code == 200


def test_dos_creaciones_simultaneas(app):
    with app.state.sessions() as session:
        repo = SQLUsuariosRepository(session)
        one = repo.add('uno@example.com', 'hash-de-prueba').id
        two = repo.add('dos@example.com', 'hash-de-prueba').id
    barrier = threading.Barrier(2)

    def reserve(uid):
        with app.state.sessions() as session:
            service = ReservaService(SQLReservasRepository(session), app.state.tokens)
            barrier.wait(timeout=10)
            try:
                service.create(uid, ReservaIn(**payload()))
                return 'creada'
            except DomainError as exc:
                return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, [one, two]))
    assert sorted(results) == ['creada', 'solapamiento']
