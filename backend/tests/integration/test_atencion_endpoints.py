import pytest
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_health_endpoint_retorna_healthy(client):
    response = client.get("/health/")
    assert response.status_code in (200, 503)
    assert "status" in response.json()


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_paginacion_default_10_max_50(api_client_coordinador):
    response = api_client_coordinador.get("/api/atenciones/", {"page_size": 50})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["page_size"] <= 50


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_listar_filtro_estado_invalido_retorna_400(api_client_coordinador):
    response = api_client_coordinador.get("/api/atenciones/", {"estado": "NO_VALIDO"})
    assert response.status_code == 400
    assert response.json()["error"] == "parametros_filtro_invalidos"


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_detalle_atencion(api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory

    atencion = AtencionFactory()
    response = api_client_coordinador.get(f"/api/atenciones/{atencion.pk}/")
    assert response.status_code == 200
    assert response.json()["id"] == atencion.pk


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@patch("atenciones.services.atencion_service.enviar_email_cliente.delay")
def test_finalizar_atencion_ok(mock_delay, api_client_consultor):
    from atenciones.constants import EstadoAtencion
    from atenciones.models import AtentionConsultant
    from tests.factories.atencion_factory import AtencionFactory

    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion.pk}/finalizar/",
        {
            "estado": EstadoAtencion.FINALIZADA,
            "notas_finales": "Notas finales válidas con más de veinte caracteres.",
        },
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == EstadoAtencion.FINALIZADA
    assert data["closing_date"] is not None
    assert data["final_note"] is not None
    mock_delay.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_finalizar_atencion_notas_cortas_retorna_400(api_client_consultor):
    from atenciones.constants import ERR_NOTAS_FINALES_OBLIGATORIAS, EstadoAtencion
    from atenciones.models import AtentionConsultant
    from tests.factories.atencion_factory import AtencionFactory

    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion.pk}/finalizar/",
        {"estado": EstadoAtencion.FINALIZADA, "notas_finales": "corta"},
        format="json",
    )
    assert response.status_code == 400
    assert (
        response.json()["field_errors"]["notas_finales"][0]
        == ERR_NOTAS_FINALES_OBLIGATORIAS
    )


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_finalizar_atencion_estado_invalido_retorna_400(api_client_consultor):
    from atenciones.constants import ERR_ESTADO_NO_PERMITIDO
    from atenciones.models import AtentionConsultant
    from tests.factories.atencion_factory import AtencionFactory

    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion.pk}/finalizar/",
        {
            "estado": "ANULADA",
            "notas_finales": "Notas finales válidas con más de veinte caracteres.",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["field_errors"]["estado"][0] == ERR_ESTADO_NO_PERMITIDO
