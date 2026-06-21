from datetime import datetime, timedelta, timezone

import pytest

from atenciones.constants import EstadoAtencion
from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    TransicionInvalidaException,
)
from atenciones.exceptions.custom_exceptions import CruceHorarioException
from atenciones.validators.atencion_validators import (
    validar_no_anterior_fecha_actual,
    validar_bloques_30min,
    validar_cruce_horario,
    validar_longitud_notas,
    validar_transicion_estado,
)


@pytest.mark.unit
def test_fecha_actual_y_futura_pasa():
    fecha_futura = datetime.now(timezone.utc) + timedelta(minutes=5)
    validar_no_anterior_fecha_actual(fecha_futura)


@pytest.mark.unit
def test_fecha_anterior_falla():
    fecha_pasada = datetime.now(timezone.utc) - timedelta(minutes=5)
    with pytest.raises(AnticipacionInsuficiente):
        validar_no_anterior_fecha_actual(fecha_pasada)


@pytest.mark.unit
def test_transicion_agendada_a_finalizada_valida():
    validar_transicion_estado(EstadoAtencion.AGENDADA, EstadoAtencion.FINALIZADA)


@pytest.mark.unit
def test_transicion_finalizada_a_anulada_invalida():
    with pytest.raises(TransicionInvalidaException):
        validar_transicion_estado(EstadoAtencion.FINALIZADA, EstadoAtencion.ANULADA)


@pytest.mark.unit
def test_longitud_notas_minima():
    with pytest.raises(TransicionInvalidaException):
        validar_longitud_notas("corta")


@pytest.mark.unit
def test_bloques_30_min_invalidos():
    inicio = datetime.now(timezone.utc).replace(minute=15, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)
    with pytest.raises(AnticipacionInsuficiente):
        validar_bloques_30min(inicio, fin)


@pytest.mark.unit
def test_cruce_horario_detectado():
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    fin = inicio + timedelta(hours=1)
    cruces = [(1, inicio, fin)]
    with pytest.raises(CruceHorarioException):
        validar_cruce_horario([1], inicio, fin, cruces)


@pytest.mark.unit
def test_cruce_horario_consultor_no_en_lista():
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    fin = inicio + timedelta(hours=1)
    cruces = [(99, inicio, fin)]
    validar_cruce_horario(
        [1], inicio + timedelta(hours=2), fin + timedelta(hours=2), cruces
    )
