import asyncio
import json
import socket
import threading
import time

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import uvicorn

from app.main import create_app
from tests.test_integration import payload


def unpack(result):
    assert not result.isError
    return result.structuredContent or json.loads(result.content[0].text)


def test_mcp_transporte_real(settings):
    app = create_app(settings)
    # Bind port 0 so the operating system safely allocates an available port.
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    port = listener.getsockname()[1]
    listener.listen(128)
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, log_level='warning'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started:
        if not thread.is_alive() or time.monotonic() > deadline:
            raise RuntimeError('El servidor MCP no inició')
        time.sleep(0.02)
    base = f'http://127.0.0.1:{port}'

    async def scenario():
        async with httpx.AsyncClient(base_url=base) as http:
            assert (await http.post('/mcp/', json={})).status_code == 401
            assert (await http.post('/mcp/', json={}, headers={
                'Authorization': 'Bearer inventado'})).status_code == 401
            for email in ('mcp@example.com', 'otro@example.com'):
                assert (await http.post('/auth/registro', json={
                    'email': email, 'password': 'Demo-12345'})).status_code == 201
            response = await http.post('/auth/token', data={'username': 'mcp@example.com',
                                                          'password': 'Demo-12345'})
            headers = {'Authorization': 'Bearer ' + response.json()['access_token']}
            async with streamablehttp_client(base + '/mcp/', headers=headers) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    assert len(tools.tools) == 6
                    assert all('usuario_id' not in t.inputSchema.get('properties', {})
                               for t in tools.tools)
                    created = unpack(await session.call_tool('crear_reserva', payload()))
                    reserva_id = created['id']
                    assert created['usuario_id'] == 1
                    listed = unpack(await session.call_tool('listar_reservas', {}))
                    assert len(listed['reservas']) == 1
                    assert (await http.get('/reservas/', headers=headers)).json()[0]['id'] == reserva_id
                    duplicate = unpack(await session.call_tool('crear_reserva', payload()))
                    assert duplicate['code'] == 'solapamiento'
                    invalid = unpack(await session.call_tool('crear_reserva', payload(fecha='bad')))
                    assert invalid['code'] == 'entrada_invalida'
                    query = unpack(await session.call_tool('consultar_reserva', {'reserva_id': reserva_id}))
                    assert query['id'] == reserva_id
                    updated = unpack(await session.call_tool('actualizar_reserva', {
                        'reserva_id': reserva_id, **payload(motivo='Actualizada desde MCP')}))
                    assert updated['version'] == 2
                    missing = unpack(await session.call_tool('consultar_reserva', {'reserva_id': 999}))
                    assert missing['code'] == 'no_encontrada'
                    prep = unpack(await session.call_tool('preparar_cancelacion', {'reserva_id': reserva_id}))
                    assert 'confirmacion' in prep
                    rejected = unpack(await session.call_tool('cancelar_reserva', {
                        'reserva_id': reserva_id, 'confirmacion': prep['confirmacion']}))
                    assert rejected['code'] == 'confirmacion_requerida'
                    cancelled = unpack(await session.call_tool('cancelar_reserva', {
                        'reserva_id': reserva_id, 'confirmacion': prep['confirmacion'], 'confirmar': True}))
                    assert cancelled['cancelada'] is True
                    assert unpack(await session.call_tool('listar_reservas', {}))['reservas'] == []
                    # Restore a reservation to test isolation from another JWT below.
                    unpack(await session.call_tool('crear_reserva', payload()))
            other = await http.post('/auth/token', data={'username': 'otro@example.com',
                                                        'password': 'Demo-12345'})
            other_headers = {'Authorization': 'Bearer ' + other.json()['access_token']}
            async with streamablehttp_client(base + '/mcp/', headers=other_headers) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    assert unpack(await session.call_tool('listar_reservas', {}))['reservas'] == []
                    assert unpack(await session.call_tool('crear_reserva', payload()))['code'] == 'solapamiento'

    try:
        asyncio.run(scenario())
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        assert not thread.is_alive()
