from datetime import datetime, timedelta

from atenciones.constants import (
    ERR_ANTICIPATION,
    ERR_ESTADO_NO_PERMITIDO,
    ERR_NOTAS_FINALES_CORTAS,
    ERR_NOTAS_FINALES_LARGAS,
    EstadoAtencion,
    VALID_TRANSACTIONS,
)
from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    CruceHorarioException,
    EstadoAtencionNoPermitidoException,
    TransicionInvalidaException,
)


def validar_anticipacion_24h(fecha_programada: datetime) -> None:
    if fecha_programada - datetime.now(tz=fecha_programada.tzinfo) < timedelta(
        hours=24
    ):
        raise AnticipacionInsuficiente(ERR_ANTICIPATION)


def validar_bloques_30min(fecha_inicio: datetime, fecha_fin: datetime) -> None:
    for dt in (fecha_inicio, fecha_fin):
        if dt.minute % 30 != 0 or dt.second != 0 or dt.microsecond != 0:
            raise AnticipacionInsuficiente(
                "Las fechas deben alinearse a bloques de 30 minutos."
            )


def validar_cruce_horario(
    consultor_ids: list[int] | list[str],
    fecha_inicio: datetime,
    fecha_fin: datetime,
    cruces_existentes: list[tuple[int, datetime, datetime]]
    | list[tuple[str, datetime, datetime]]
    | None = None,
) -> None:
    cruces_existentes = cruces_existentes or []
    for consultor_id, inicio, fin in cruces_existentes:
        if consultor_id not in consultor_ids:
            continue
        if fecha_inicio < fin and fecha_fin > inicio:
            raise CruceHorarioException()


def validar_transicion_estado(estado_actual: str, nuevo_estado: str) -> None:
    permitidos = VALID_TRANSACTIONS.get(estado_actual, [])
    if nuevo_estado not in permitidos:
        raise TransicionInvalidaException()


def validar_estado_finalizacion(estado: str) -> None:
    if estado != EstadoAtencion.FINALIZADA:
        raise EstadoAtencionNoPermitidoException(ERR_ESTADO_NO_PERMITIDO)


def validar_transicion_a_finalizada(estado_actual: str) -> None:
    permitidos = VALID_TRANSACTIONS.get(estado_actual, [])
    if EstadoAtencion.FINALIZADA not in permitidos:
        raise EstadoAtencionNoPermitidoException(ERR_ESTADO_NO_PERMITIDO)


def validar_longitud_notas(
    notas_finales: str, minimo: int = 20, maximo: int = 2000
) -> None:
    contenido = notas_finales.strip()
    if len(contenido) < minimo:
        raise EstadoAtencionNoPermitidoException(ERR_NOTAS_FINALES_CORTAS)
    if len(notas_finales) > maximo:
        raise EstadoAtencionNoPermitidoException(ERR_NOTAS_FINALES_LARGAS)
