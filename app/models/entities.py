from datetime import date, time

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = 'usuarios'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(100))


class Reserva(Base):
    __tablename__ = 'reservas'
    # Never recycle a cancelled ID: an old confirmation must not target a new reservation.
    __table_args__ = (Index('ix_reserva_conflicto', 'laboratorio_id', 'fecha'),
                      {'sqlite_autoincrement': True})
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    laboratorio_id: Mapped[int]
    fecha: Mapped[date]
    hora_inicio: Mapped[time]
    hora_fin: Mapped[time]
    motivo: Mapped[str] = mapped_column(String(200))
    version: Mapped[int] = mapped_column(default=1)
