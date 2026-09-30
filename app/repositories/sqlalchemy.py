from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Reserva, Usuario
from app.schemas.reservas import ReservaIn
from app.utils.errors import DomainError


class SQLUsuariosRepository:
    def __init__(self, session: Session):
        self.session = session

    def by_email(self, email):
        return self.session.scalar(select(Usuario).where(Usuario.email == email))

    def by_id(self, user_id):
        return self.session.get(Usuario, user_id)

    def add(self, email, password_hash):
        user = Usuario(email=email, password_hash=password_hash)
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            # Maps the persistence uniqueness violation; policy remains in AuthService.
            raise DomainError('El email ya está registrado', 'email_duplicado', 409) from exc
        return user


class SQLReservasRepository:
    def __init__(self, session: Session):
        self.session = session

    @contextmanager
    def atomic(self):
        # Authentication may already have started this transaction. Reuse it.
        try:
            yield
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def own(self, reserva_id, usuario_id):
        return self.session.scalar(select(Reserva).where(
            Reserva.id == reserva_id, Reserva.usuario_id == usuario_id))

    def list_own(self, usuario_id, skip, limit):
        stmt = select(Reserva).where(Reserva.usuario_id == usuario_id).order_by(
            Reserva.fecha, Reserva.hora_inicio, Reserva.id).offset(skip).limit(limit)
        return list(self.session.scalars(stmt))

    def overlaps(self, laboratorio_id, fecha, inicio, fin, excluding=None):
        stmt = select(Reserva.id).where(
            Reserva.laboratorio_id == laboratorio_id, Reserva.fecha == fecha,
            Reserva.hora_inicio < fin, Reserva.hora_fin > inicio)
        if excluding is not None:
            stmt = stmt.where(Reserva.id != excluding)
        return self.session.scalar(stmt.limit(1)) is not None

    def add(self, usuario_id, data: ReservaIn):
        reserva = Reserva(usuario_id=usuario_id, **data.model_dump(), version=1)
        self.session.add(reserva)
        self.session.flush()
        return reserva

    def update(self, reserva, data: ReservaIn):
        for name, value in data.model_dump().items():
            setattr(reserva, name, value)
        reserva.version += 1
        self.session.flush()
        return reserva

    def delete(self, reserva):
        self.session.delete(reserva)
        self.session.flush()
