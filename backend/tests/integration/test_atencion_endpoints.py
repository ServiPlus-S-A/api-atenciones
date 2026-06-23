import pytest
from datetime import datetime, timedelta, timezone

from atenciones.models import Atencion


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_health_endpoint_retorna_healthy(client):
    response = client.get("/health/", HTTP_ACCEPT="application/json")
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
def test_listar_atenciones_con_filtros_hu12(api_client_coordinador):
    from atenciones.models import AtentionConsultant
    from tests.factories.atencion_factory import AtencionFactory

    atencion = AtencionFactory(request_id=321, customer_name="Cliente Norte")
    AtentionConsultant.objects.create(
        atention=atencion,
        consultant_id="consultor-1",
        consultant_name="Maria Gomez",
        is_leader=True,
    )

    response = api_client_coordinador.get(
        "/api/atenciones/",
        {
            "solicitud_id": "321",
            "nombre_cliente": "norte",
            "nombre_consultor": "maria",
            "fecha_registro": atencion.created_at.date().isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == atencion.pk
    assert data["results"][0]["customer_name"] == "Cliente Norte"


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
