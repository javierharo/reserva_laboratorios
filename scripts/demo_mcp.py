"""Official MCP client: lists tools and demonstrates the authenticated transport."""
import argparse
import asyncio
from datetime import datetime, timedelta
from getpass import getpass
import json
import secrets
from zoneinfo import ZoneInfo

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def unpack(result):
    if result.isError:
        raise RuntimeError(result.content)
    return result.structuredContent or json.loads(result.content[0].text)


async def run(args):
    async with httpx.AsyncClient(base_url=args.url, timeout=30) as http:
        if args.demo:
            email = 'mcp-' + secrets.token_hex(6) + '@example.com'
            password = secrets.token_urlsafe(18)
            response = await http.post('/auth/registro', json={'email': email, 'password': password})
            response.raise_for_status()
            print('Cuenta de demostración creada; credenciales y JWT no se muestran.')
        else:
            email = input('Email registrado: ').strip()
            password = getpass('Contraseña: ')
        response = await http.post('/auth/token', data={'username': email, 'password': password})
        response.raise_for_status()
        headers = {'Authorization': 'Bearer ' + response.json()['access_token']}
        async with streamablehttp_client(args.url.rstrip('/') + '/mcp/', headers=headers) as streams:
            read, write, _ = streams
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print('Tools MCP:', ', '.join(t.name for t in tools.tools))
                print('Mis reservas:', unpack(await session.call_tool('listar_reservas', {})))
                if not args.demo:
                    return
                day = (datetime.now(ZoneInfo('America/Guayaquil')) + timedelta(days=1)).date().isoformat()
                for hour in range(8, 18):
                    data = {'laboratorio_id': 2, 'fecha': day, 'hora_inicio': f'{hour:02d}:00',
                            'hora_fin': f'{hour + 1:02d}:00', 'motivo': 'Demo MCP'}
                    row = unpack(await session.call_tool('crear_reserva', data))
                    if 'id' in row:
                        break
                    if row.get('code') != 'solapamiento':
                        raise RuntimeError(row)
                else:
                    raise RuntimeError('No hay horario libre mañana en laboratorio 2.')
                print('Crear desde MCP:', row)
                rejected = unpack(await session.call_tool('crear_reserva', data))
                assert rejected.get('code') == 'solapamiento'
                print('Rechazo esperado:', rejected)
                rest = await http.get('/reservas/', headers=headers)
                rest.raise_for_status()
                assert row['id'] in [r['id'] for r in rest.json()]
                print('REST muestra la misma reserva: comprobado.')
                prep = unpack(await session.call_tool('preparar_cancelacion', {'reserva_id': row['id']}))
                print('Resumen de cancelación:', prep['reserva'])
                if input('¿Confirmas cancelar ESTA reserva de demo? Escribe SI: ').strip().upper() == 'SI':
                    result = unpack(await session.call_tool('cancelar_reserva', {
                        'reserva_id': row['id'], 'confirmacion': prep['confirmacion'], 'confirmar': True}))
                    print('Resultado:', result)
                else:
                    print('La reserva de demo se conserva. No se canceló.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--demo', action='store_true',
                        help='Crea usuario y reserva de prueba; solicita confirmación antes de cancelar')
    asyncio.run(run(parser.parse_args()))


if __name__ == '__main__':
    main()
