import pytest


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
