from contextlib import nullcontext

from app.models.entities import Reserva, Usuario


class FakeUsuarios:
    def __init__(self):
        self.users = {}

    def by_email(self, email):
        return next((u for u in self.users.values() if u.email == email), None)

    def by_id(self, user_id):
        return self.users.get(user_id)

    def add(self, email, password_hash):
        user = Usuario(id=len(self.users) + 1, email=email, password_hash=password_hash)
        self.users[user.id] = user
        return user


class FakeReservas:
    def __init__(self):
        self.rows = {}
        self.next_id = 1

    def atomic(self):
        return nullcontext()

    def own(self, reserva_id, usuario_id):
        row = self.rows.get(reserva_id)
        return row if row and row.usuario_id == usuario_id else None

    def list_own(self, usuario_id, skip, limit):
        rows = sorted((x for x in self.rows.values() if x.usuario_id == usuario_id),
                      key=lambda x: (x.fecha, x.hora_inicio, x.id))
        return rows[skip:skip + limit]

    def overlaps(self, laboratorio_id, fecha, inicio, fin, excluding=None):
        return any(x.id != excluding and x.laboratorio_id == laboratorio_id
                   and x.fecha == fecha and x.hora_inicio < fin and x.hora_fin > inicio
                   for x in self.rows.values())

    def add(self, usuario_id, data):
        row = Reserva(id=self.next_id, usuario_id=usuario_id, version=1, **data.model_dump())
        self.rows[row.id] = row
        self.next_id += 1
        return row

    def update(self, row, data):
        for k, v in data.model_dump().items():
            setattr(row, k, v)
        row.version += 1
        return row

    def delete(self, row):
        del self.rows[row.id]
