from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler

from app.mcp.server import MCPAuthMiddleware, build_mcp
from app.routers.auth import router as auth_router
from app.routers.reservas import router as reservas_router
from app.utils.config import Settings
from app.utils.database import create_database
from app.utils.errors import DomainError
from app.utils.security import TokenManager


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    engine, sessions = create_database(settings.database_url)
    tokens = TokenManager(settings)
    mcp = build_mcp(sessions, tokens)
    mcp_app = mcp.streamable_http_app()

    @asynccontextmanager
    async def lifespan(app):
        async with mcp.session_manager.run():
            yield
        engine.dispose()

    app = FastAPI(title='Reservas de laboratorios', version='1.0.0', lifespan=lifespan,
                  description='Proyecto integrador: REST y MCP con servicios compartidos.')
    app.state.sessions = sessions
    app.state.tokens = tokens
    app.state.engine = engine
    app.state.mcp = mcp

    @app.exception_handler(DomainError)
    async def domain_handler(request: Request, exc: DomainError):
        headers = {'WWW-Authenticate': 'Bearer'} if exc.status == 401 else None
        error = HTTPException(status_code=exc.status,
                              detail={'error': str(exc), 'code': exc.code}, headers=headers)
        return await http_exception_handler(request, error)

    @app.get('/health', tags=['Estado'])
    def health():
        return {'status': 'ok'}

    app.include_router(auth_router)
    app.include_router(reservas_router)
    app.mount('/mcp', MCPAuthMiddleware(mcp_app, sessions, tokens))
    return app
