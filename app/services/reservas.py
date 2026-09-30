from datetime import date, datetime
from typing import Callable
from zoneinfo import ZoneInfo

from app.repositories.contracts import ReservasRepository
from app.schemas.reservas import PreparacionOut, ReservaIn, ReservaOut
from app.utils.errors import DomainError, NotFound
from app.utils.security import TokenManager

LABORATORIOS = {1: 'Computación', 2: 'Redes', 3: 'Telecomunicaciones'}


def today_ecuador() -> date:
    return datetime.now(ZoneInfo('America/Guayaquil')).date()


class ReservaService:
    def __init__(self, repository: ReservasRepository, tokens: TokenManager,
                 today: Callable[[], date] = today_ecuador):
        self.repository = repository
        self.tokens = tokens
        self.today = today

    def _validate(self, data: ReservaIn):
        if data.hora_fin <= data.hora_inicio:
            raise DomainError('La hora final debe ser posterior a la inicial', 'horario_invalido')
        if data.fecha < self.today():
            raise DomainError('La fecha no puede ser anterior al día actual', 'fecha_pasada')
        if data.laboratorio_id not in LABORATORIOS:
            raise DomainError('El laboratorio no existe', 'laboratorio_invalido')

    def _check_overlap(self, data: ReservaIn, excluding=None):
        if self.repository.overlaps(data.laboratorio_id, data.fecha, data.hora_inicio,
                                    data.hora_fin, excluding):
            raise DomainError('El laboratorio ya está reservado en ese horario', 'solapamiento', 409)

    def get(self, usuario_id: int, reserva_id: int) -> ReservaOut:
        reserva = self.repository.own(reserva_id, usuario_id)
        if reserva is None:
            raise NotFound()
        return ReservaOut.model_validate(reserva)

    def list(self, usuario_id: int, skip: int = 0, limit: int = 20) -> list[ReservaOut]:
        if skip < 0 or not 1 <= limit <= 100:
            raise DomainError('Paginación inválida', 'paginacion_invalida')
        return [ReservaOut.model_validate(x)
                for x in self.repository.list_own(usuario_id, skip, limit)]

    def create(self, usuario_id: int, data: ReservaIn) -> ReservaOut:
        self._validate(data)
        with self.repository.atomic():
            self._check_overlap(data)
            result = ReservaOut.model_validate(self.repository.add(usuario_id, data))
        return result

    def update(self, usuario_id: int, reserva_id: int, data: ReservaIn) -> ReservaOut:
        with self.repository.atomic():
            reserva = self.repository.own(reserva_id, usuario_id)
            if reserva is None:
                raise NotFound()
            self._validate(data)
            self._check_overlap(data, excluding=reserva_id)
            result = ReservaOut.model_validate(self.repository.update(reserva, data))
        return result

    def prepare_cancel(self, usuario_id: int, reserva_id: int) -> PreparacionOut:
        reserva = self.get(usuario_id, reserva_id)
        confirmation = self.tokens.issue(usuario_id, purpose='cancel',
                                         reserva_id=reserva_id, version=reserva.version)
        return PreparacionOut(reserva=reserva, confirmacion=confirmation,
                              expira_en_segundos=self.tokens.settings.confirmation_seconds)

    def cancel(self, usuario_id: int, reserva_id: int, confirmation: str, confirmar: bool):
        if not confirmar:
            raise DomainError('Debes confirmar explícitamente la cancelación', 'confirmacion_requerida')
        claims = self.tokens.decode(confirmation, purpose='cancel')
        with self.repository.atomic():
            reserva = self.repository.own(reserva_id, usuario_id)
            if reserva is None:
                raise NotFound()
            if (claims['sub'] != str(usuario_id) or claims.get('reserva_id') != reserva_id
                    or claims.get('version') != reserva.version):
                raise DomainError('La confirmación no corresponde a esta reserva vigente',
                                  'confirmacion_invalida')
            self.repository.delete(reserva)
