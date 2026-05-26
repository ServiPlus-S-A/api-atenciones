from unittest.mock import patch

import pytest

from atenciones.constants import EstadoAtencion
from atenciones.exceptions.custom_exceptions import AnticipacionInsuficiente, TransicionInvalidaException
from atenciones.integrations.solicitudes_client import SolicitudInfo
from atenciones.services.atencion_service import AtencionService
from tests.factories.atencion_factory import AtencionFactory, AtencionFinalizadaFactory


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.get")
@patch("atenciones.services.atencion_service.parametrizacion_client.get")
def test_crear_valida_solicitud_pendiente(mock_param, mock_sol, api_client_coordinador):
    mock_sol.return_value = SolicitudInfo(id=1, estado="Pendiente", consultor_ids=[1])
    from atenciones.integrations.parametrizacion_client import ConsultorInfo

    mock_param.return_value = ConsultorInfo(id=1, disponible=True, aptitudes=[])
    user = api_client_coordinador.test_user
    dto = AtencionService.crear(
        {
            "solicitud_id": 1,
            "consultor_ids": [1],
            "mensaje_preliminar": "Mensaje preliminar de prueba.",
        },
        user,
    )
    assert dto.estado == EstadoAtencion.AGENDADA


@pytest.mark.django_db
def test_transicion_invalida_finalizada_a_anulada(api_client_coordinador):
    atencion = AtencionFinalizadaFactory()
    user = api_client_coordinador.test_user
    with pytest.raises(TransicionInvalidaException):
        AtencionService.anular(
            atencion.pk,
            {"motivo_anulacion": "Motivo válido de anulación."},
            user,
        )


@pytest.mark.django_db
def test_programar_falla_menos_24h(api_client_coordinador):
    from datetime import datetime, timedelta, timezone

    atencion = AtencionFactory()
    user = api_client_coordinador.test_user
    inicio = datetime.now(timezone.utc) + timedelta(hours=2)
    fin = inicio + timedelta(hours=1)
    with pytest.raises(AnticipacionInsuficiente):
        AtencionService.programar(
            atencion.pk,
            {"fecha_programada": inicio, "fecha_fin": fin},
            user,
        )
