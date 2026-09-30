"""Demo local reproducible; no keys or passwords are printed."""
import argparse
from datetime import datetime, timedelta
import secrets
from zoneinfo import ZoneInfo

import httpx


def main():
    parser = argparse.ArgumentParser(description='Demuestra CRUD REST y conflicto entre usuarios')
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    day = (datetime.now(ZoneInfo('America/Guayaquil')) + timedelta(days=1)).date().isoformat()
    with httpx.Client(base_url=args.url, timeout=30) as http:
        headers = []
        for _ in range(2):
            email = 'rest-' + secrets.token_hex(6) + '@example.com'
            password = secrets.token_urlsafe(18)
            http.post('/auth/registro', json={'email': email, 'password': password}).raise_for_status()
            response = http.post('/auth/token', data={'username': email, 'password': password})
            response.raise_for_status()
            headers.append({'Authorization': 'Bearer ' + response.json()['access_token']})
        alice, bob = headers
        response = http.get('/reservas/')
        assert response.status_code == 401
        print('Sin token: 401')
        for hour in range(8, 18):
            data = {'laboratorio_id': 1, 'fecha': day, 'hora_inicio': f'{hour:02d}:00',
                    'hora_fin': f'{hour + 1:02d}:00', 'motivo': 'Demo REST'}
            response = http.post('/reservas/', json=data, headers=alice)
            if response.status_code == 201:
                break
            if response.status_code != 409:
                response.raise_for_status()
        else:
            raise RuntimeError('No hay horario libre mañana; usa una base local de demostración.')
        row_id = response.json()['id']
        print(f'Crear: 201, reserva {row_id}; laboratorio 1, {day}, {data["hora_inicio"]}')
        response = http.post('/reservas/', json=data, headers=bob)
        assert response.status_code == 409
        print('Solapamiento de otro usuario: 409')
        response = http.get(f'/reservas/{row_id}', headers=bob)
        assert response.status_code == 404
        print('Acceso de otro usuario: 404')
        response = http.get(f'/reservas/{row_id}', headers=alice)
        response.raise_for_status()
        print('Consultar propia: 200')
        response = http.get('/reservas/', headers=alice)
        response.raise_for_status()
        print(f'Listar: 200, {len(response.json())} reserva(s)')
        data['motivo'] = 'Demo REST actualizada'
        response = http.put(f'/reservas/{row_id}', json=data, headers=alice)
        response.raise_for_status()
        print('Actualizar: 200, versión', response.json()['version'])
        prep = http.post(f'/reservas/{row_id}/preparar-cancelacion', headers=alice)
        prep.raise_for_status()
        print('Reserva a cancelar:', prep.json()['reserva'])
        if input('¿Confirmas cancelar ESTA reserva de demo? Escribe SI: ').strip().upper() == 'SI':
            response = http.delete(f'/reservas/{row_id}', params={'confirmar': 'true'},
                                   headers={**alice, 'X-Confirmacion': prep.json()['confirmacion']})
            assert response.status_code == 204
            print('Cancelar: 204. Demo REST completada.')
        else:
            print('La reserva de demo se conserva. No se canceló.')


if __name__ == '__main__':
    main()
