from datetime import datetime, timedelta, timezone

import pytest

from atenciones.constants import EstadoAtencion
from atenciones.exceptions.custom_exceptions import AnticipacionInsuficiente, TransicionInvalidaException
from atenciones.validators.atencion_validators import (
    validar_anticipacion_24h,
    validar_longitud_notas,
    validar_transicion_estado,
)


@pytest.mark.unit
def test_anticipacion_exactamente_24h_pasa():
    fecha = datetime.now(timezone.utc) + timedelta(hours=24, minutes=1)
    validar_anticipacion_24h(fecha)


@pytest.mark.unit
def test_anticipacion_23h59m_falla():
    fecha = datetime.now(timezone.utc) + timedelta(hours=23, minutes=59)
    with pytest.raises(AnticipacionInsuficiente):
        validar_anticipacion_24h(fecha)


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
