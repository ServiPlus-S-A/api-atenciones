from datetime import datetime

from atenciones.constants import ERR_ANTICIPATION, VALID_TRANSACTIONS
from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    CruceHorarioException,
    TransicionInvalidaException,
)


def validar_no_anterior_fecha_actual(fecha_programada: datetime) -> None:
    if fecha_programada < datetime.now(tz=fecha_programada.tzinfo):
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
    cruzados = []
    str_consultor_ids = [str(cid) for cid in consultor_ids]
    for consultor_id, inicio, fin in cruces_existentes:
        if str(consultor_id) not in str_consultor_ids:
            continue
        if fecha_inicio < fin and fecha_fin > inicio:
            cruzados.append({
                "consultor_id": str(consultor_id),
                "fecha_inicio": inicio.isoformat(),
                "fecha_fin": fin.isoformat()
            })
    if cruzados:
        raise CruceHorarioException(cruces=cruzados)


def validar_transicion_estado(estado_actual: str, nuevo_estado: str) -> None:
    permitidos = VALID_TRANSACTIONS.get(estado_actual, [])
    if nuevo_estado not in permitidos:
        raise TransicionInvalidaException()


def validar_longitud_notas(notas_finales: str, minimo: int = 20) -> None:
    if len(notas_finales.strip()) < minimo:
        from atenciones.constants import ERR_MINIMUM_FINAL_NOTE

        raise TransicionInvalidaException(ERR_MINIMUM_FINAL_NOTE)
