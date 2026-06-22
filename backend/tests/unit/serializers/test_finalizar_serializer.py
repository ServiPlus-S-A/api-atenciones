import pytest
from rest_framework.exceptions import ValidationError

from atenciones.constants import (
    ERR_ESTADO_NO_PERMITIDO,
    ERR_NOTAS_FINALES_LARGAS,
    ERR_NOTAS_FINALES_OBLIGATORIAS,
    EstadoAtencion,
)
from atenciones.serializers.input.finalizar_atencion_input_serializer import (
    FinalizarAtencionInputSerializer,
)


def _payload(notas: str, estado: str = EstadoAtencion.FINALIZADA) -> dict:
    return {"estado": estado, "notas_finales": notas}


@pytest.mark.unit
def test_finalizar_serializer_valido():
    ser = FinalizarAtencionInputSerializer(
        data=_payload("Notas finales válidas con más de veinte caracteres.")
    )
    assert ser.is_valid(), ser.errors


@pytest.mark.unit
def test_finalizar_serializer_rechaza_estado_invalido():
    ser = FinalizarAtencionInputSerializer(
        data=_payload("Notas finales válidas con más de veinte caracteres.", "ANULADA")
    )
    with pytest.raises(ValidationError) as exc:
        ser.is_valid(raise_exception=True)
    assert exc.value.detail["estado"][0] == ERR_ESTADO_NO_PERMITIDO


@pytest.mark.unit
def test_finalizar_serializer_rechaza_notas_cortas():
    ser = FinalizarAtencionInputSerializer(data=_payload("corta"))
    with pytest.raises(ValidationError) as exc:
        ser.is_valid(raise_exception=True)
    assert exc.value.detail["notas_finales"][0] == ERR_NOTAS_FINALES_OBLIGATORIAS


@pytest.mark.unit
def test_finalizar_serializer_rechaza_notas_vacias():
    ser = FinalizarAtencionInputSerializer(
        data={"estado": EstadoAtencion.FINALIZADA, "notas_finales": ""}
    )
    with pytest.raises(ValidationError) as exc:
        ser.is_valid(raise_exception=True)
    assert exc.value.detail["notas_finales"][0] == ERR_NOTAS_FINALES_OBLIGATORIAS


@pytest.mark.unit
def test_finalizar_serializer_rechaza_notas_largas():
    ser = FinalizarAtencionInputSerializer(data=_payload("x" * 2001))
    with pytest.raises(ValidationError) as exc:
        ser.is_valid(raise_exception=True)
    assert exc.value.detail["notas_finales"][0] == ERR_NOTAS_FINALES_LARGAS


@pytest.mark.unit
def test_finalizar_serializer_rechaza_notas_solo_espacios():
    ser = FinalizarAtencionInputSerializer(data=_payload(" " * 25))
    with pytest.raises(ValidationError) as exc:
        ser.is_valid(raise_exception=True)
    assert exc.value.detail["notas_finales"][0] == ERR_NOTAS_FINALES_OBLIGATORIAS
