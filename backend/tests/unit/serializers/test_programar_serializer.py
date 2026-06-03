from datetime import datetime, timedelta, timezone

import pytest
from rest_framework.exceptions import ValidationError

from atenciones.serializers.input.programar_atencion_input_serializer import ProgramarAtencionInputSerializer


def _fechas_validas():
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(minutes=30)
    return inicio, fin


@pytest.mark.unit
def test_programar_serializer_valido():
    inicio, fin = _fechas_validas()
    ser = ProgramarAtencionInputSerializer(data={"fecha_programada": inicio, "fecha_fin": fin})
    assert ser.is_valid(), ser.errors


@pytest.mark.unit
def test_programar_serializer_fin_anterior_a_inicio():
    inicio, fin = _fechas_validas()
    ser = ProgramarAtencionInputSerializer(data={"fecha_programada": fin, "fecha_fin": inicio})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)


@pytest.mark.unit
def test_programar_serializer_bloques_30_min():
    inicio, fin = _fechas_validas()
    inicio = inicio.replace(minute=15)
    ser = ProgramarAtencionInputSerializer(data={"fecha_programada": inicio, "fecha_fin": fin})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)
