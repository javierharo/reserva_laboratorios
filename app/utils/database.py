from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.models.entities import Base


def create_database(url: str):
    engine = create_engine(url, connect_args={'check_same_thread': False, 'timeout': 15})

    @event.listens_for(engine, 'connect')
    def set_sqlite_options(connection, _):
        # Explicit BEGIN is controlled by the repository, including reads/writes.
        connection.isolation_level = None
        connection.execute('PRAGMA foreign_keys=ON')

    @event.listens_for(engine, 'begin')
    def begin(connection):
        # Reservas is a small local MVP: all transactions serialize to prevent overlap races.
        connection.exec_driver_sql('BEGIN IMMEDIATE')

    Base.metadata.create_all(engine)
    return engine, sessionmaker(engine, expire_on_commit=False)
