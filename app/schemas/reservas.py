from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReservaIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    laboratorio_id: int = Field(gt=0, strict=True)
    fecha: date
    hora_inicio: time
    hora_fin: time
    motivo: str = Field(min_length=1, max_length=200)

    @field_validator('motivo')
    @classmethod
    def clean_motivo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('El motivo no puede estar vacío')
        return value

    @field_validator('hora_inicio', 'hora_fin')
    @classmethod
    def local_time(cls, value: time) -> time:
        if value.tzinfo is not None or value.microsecond:
            raise ValueError('Usa horas locales sin zona ni fracciones de segundo')
        return value


class ReservaOut(ReservaIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    version: int


class PreparacionOut(BaseModel):
    reserva: ReservaOut
    confirmacion: str
    expira_en_segundos: int
    instruccion: str = 'Revisa la reserva y confirma su cancelación antes de usar este token.'
