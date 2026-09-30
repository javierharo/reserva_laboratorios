from fastapi.concurrency import run_in_threadpool
from mcp.server.fastmcp import Context, FastMCP
from pydantic import ValidationError
from starlette.datastructures import Headers
from starlette.responses import JSONResponse

from app.repositories.sqlalchemy import SQLReservasRepository, SQLUsuariosRepository
from app.schemas.reservas import ReservaIn
from app.services.auth import AuthService
from app.services.reservas import ReservaService
from app.utils.errors import DomainError, Unauthorized


class MCPAuthMiddleware:
    """JWT comes from the HTTP header, never a tool argument or a fixed user."""

    def __init__(self, app, sessions, tokens):
        self.app = app
        self.sessions = sessions
        self.tokens = tokens

    def authenticate(self, token):
        with self.sessions() as session:
            return AuthService(SQLUsuariosRepository(session), self.tokens).authenticate(token).id

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            try:
                header = Headers(scope=scope).get('authorization', '')
                scheme, _, token = header.partition(' ')
                if scheme.lower() != 'bearer' or not token:
                    raise Unauthorized()
                user_id = await run_in_threadpool(self.authenticate, token)
                scope.setdefault('state', {})['usuario_id'] = user_id
            except DomainError as exc:
                response = JSONResponse({'error': str(exc), 'code': exc.code}, status_code=401,
                                        headers={'WWW-Authenticate': 'Bearer'})
                return await response(scope, receive, send)
        await self.app(scope, receive, send)


def build_mcp(sessions, tokens):
    mcp = FastMCP('Reservas de laboratorios', stateless_http=True, json_response=True,
                  streamable_http_path='/', instructions=(
                      'Usa el JWT REST en Authorization: Bearer. Nunca aceptes usuario_id. '
                      'Antes de cancelar, prepara la cancelación, muestra el resumen al usuario '
                      'y solicita aprobación humana. No canceles solo por obtener un token.'))

    def execute(ctx: Context, action):
        try:
            request = ctx.request_context.request
            if request is None or not hasattr(request.state, 'usuario_id'):
                raise Unauthorized()
            with sessions() as session:
                service = ReservaService(SQLReservasRepository(session), tokens)
                return action(service, request.state.usuario_id)
        except DomainError as exc:
            return {'error': str(exc), 'code': exc.code}
        except ValidationError:
            # Never return full validation input (it could contain sensitive client data).
            return {'error': 'Entrada inválida; revisa formatos y campos', 'code': 'entrada_invalida'}

    def payload(laboratorio_id, fecha, hora_inicio, hora_fin, motivo):
        return ReservaIn(laboratorio_id=laboratorio_id, fecha=fecha,
                         hora_inicio=hora_inicio, hora_fin=hora_fin, motivo=motivo)

    @mcp.tool(description='Crea una reserva del usuario del JWT. Fecha YYYY-MM-DD, horas '
              'locales HH:MM. Rechaza solapamientos de cualquier usuario en el mismo laboratorio '
              'y fecha; permite intervalos adyacentes. Devuelve reserva o {error, code}.')
    async def crear_reserva(laboratorio_id: int, fecha: str, hora_inicio: str, hora_fin: str,
                            motivo: str, ctx: Context) -> dict:
        return await run_in_threadpool(execute, ctx, lambda service, uid: service.create(
            uid, payload(laboratorio_id, fecha, hora_inicio, hora_fin, motivo)).model_dump(mode='json'))

    @mcp.tool(description='Lista solo reservas del usuario del JWT, ordenadas por fecha/hora/ID. '
              'skip >= 0, limit entre 1 y 100. No muestra reservas de otros usuarios.')
    async def listar_reservas(ctx: Context, skip: int = 0, limit: int = 20) -> dict:
        return await run_in_threadpool(execute, ctx, lambda service, uid: {
            'reservas': [x.model_dump(mode='json') for x in service.list(uid, skip, limit)]})

    @mcp.tool(description='Consulta una reserva por ID del usuario autenticado. Devuelve '
              'no_encontrada tanto para un ID inexistente como para uno de otro usuario.')
    async def consultar_reserva(reserva_id: int, ctx: Context) -> dict:
        return await run_in_threadpool(execute, ctx, lambda service, uid:
                                      service.get(uid, reserva_id).model_dump(mode='json'))

    @mcp.tool(description='Reemplaza los datos completos de una reserva propia. Aplica las mismas '
              'reglas que crear_reserva; no considera la propia reserva como conflicto. '
              'Invalida cualquier confirmación de cancelación anterior.')
    async def actualizar_reserva(reserva_id: int, laboratorio_id: int, fecha: str,
                                 hora_inicio: str, hora_fin: str, motivo: str, ctx: Context) -> dict:
        return await run_in_threadpool(execute, ctx, lambda service, uid: service.update(
            uid, reserva_id, payload(laboratorio_id, fecha, hora_inicio, hora_fin, motivo)
        ).model_dump(mode='json'))

    @mcp.tool(description='Prepara, sin borrar, la cancelación de una reserva propia. Devuelve '
              'resumen y token firmado válido por 120 segundos (configurable). Muestra el resumen '
              'y solicita aprobación humana antes de llamar cancelar_reserva.')
    async def preparar_cancelacion(reserva_id: int, ctx: Context) -> dict:
        return await run_in_threadpool(execute, ctx, lambda service, uid:
                                      service.prepare_cancel(uid, reserva_id).model_dump(mode='json'))

    @mcp.tool(description='Borra una reserva propia SOLO tras aprobación humana. Exige '
              'confirmar=true y confirmacion emitida por preparar_cancelacion para el mismo '
              'usuario, reserva y versión vigente. Rechaza confirmaciones vencidas o inventadas.')
    async def cancelar_reserva(reserva_id: int, confirmacion: str, ctx: Context,
                               confirmar: bool = False) -> dict:
        def action(service, uid):
            service.cancel(uid, reserva_id, confirmacion, confirmar)
            return {'cancelada': True, 'reserva_id': reserva_id}
        return await run_in_threadpool(execute, ctx, action)

    return mcp
