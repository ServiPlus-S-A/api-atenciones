import pytest
from datetime import datetime, timedelta, timezone

from atenciones.models import Atencion
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
    assert data["page_size"] == 50
    assert data["page"] == 1
    assert data["total_pages"] == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_paginacion_limita_page_size_mayor_a_50(api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory

    for _ in range(3):
        AtencionFactory()

    response = api_client_coordinador.get("/api/atenciones/", {"page_size": 100})
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 50
    assert data["page"] == 1


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_paginacion_cambia_paginas_y_devuelve_orden_descendente(api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory

    newer = AtencionFactory()
    older = AtencionFactory()
    Atencion.objects.filter(pk=older.pk).update(
        created_at=datetime.now(timezone.utc) - timedelta(days=2)
    )
    Atencion.objects.filter(pk=newer.pk).update(
        created_at=datetime.now(timezone.utc) - timedelta(days=1)
    )

    response = api_client_coordinador.get(
        "/api/atenciones/", {"page_size": 1, "page": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["total_pages"] == 2
    assert data["results"][0]["id"] == newer.pk

    second_page = api_client_coordinador.get(
        "/api/atenciones/", {"page_size": 1, "page": 2}
    )
    assert second_page.status_code == 200
    assert second_page.json()["results"][0]["id"] == older.pk


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_listar_vacio_retorna_lista_vacia(api_client_coordinador):
    response = api_client_coordinador.get("/api/atenciones/")
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["count"] == 0
    assert data["page"] == 1
    assert data["total_pages"] == 0


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
    response = api_client_coordinador.get(
        f"/api/atenciones/{atencion.pk}/",
        HTTP_X_USER_ID="coord-uuid-099",
        HTTP_X_USER_ROLE="COORDINADOR",
    )
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
