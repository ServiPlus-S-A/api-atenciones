import pytest


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_filtrar_por_request_id(api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory

    AtencionFactory(request_id="ABC123")

    resp = api_client_coordinador.get("/api/atenciones/", {"request_id": "ABC123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["results"][0]["request_id"] == "ABC123"


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_filtrar_por_cliente_nombre_resuelve_request_ids(
    monkeypatch, api_client_coordinador
):
    from tests.factories.atencion_factory import AtencionFactory

    AtencionFactory(request_id="R1")
    AtencionFactory(request_id="R2")

    # Mock the solicitudes lookup used by the service
    monkeypatch.setattr(
        "atenciones.services.atencion_service.solicitudes_client.buscar_solicitudes_por_cliente_nombre",
        lambda nombre: ["R2"],
    )

    resp = api_client_coordinador.get("/api/atenciones/", {"cliente_nombre": "Juan"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["results"][0]["request_id"] == "R2"


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_filtrar_por_consultor_nombre_resuelve_ids(monkeypatch, api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory
    from atenciones.models import AtentionConsultant

    a1 = AtencionFactory()
    a2 = AtencionFactory()

    # Asociar consultores a atenciones
    AtentionConsultant.objects.create(atention=a1, consultant_id="10", is_leader=True)
    AtentionConsultant.objects.create(atention=a2, consultant_id="20", is_leader=True)

    # Mock parametrizacion lookup
    monkeypatch.setattr(
        "atenciones.services.atencion_service.parametrizacion_client.buscar_consultores_por_nombre",
        lambda nombre: ["20"],
    )

    resp = api_client_coordinador.get("/api/atenciones/", {"consultor_nombre": "Perez"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    # Ensure the returned atencion contains consultant 20
    consultants = data["results"][0]["consultants"]
    assert any(c["id"] == "20" for c in consultants)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_filtrar_por_fecha_registro(api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory
    from django.utils import timezone
    
    today = timezone.now().date()
    at = AtencionFactory(created_at=timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    ))
    
    resp = api_client_coordinador.get(
        "/api/atenciones/", {"fecha_registro": today.isoformat()}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_filtrar_cliente_nombre_sin_resultados(monkeypatch, api_client_coordinador):
    from tests.factories.atencion_factory import AtencionFactory

    AtencionFactory()

    monkeypatch.setattr(
        "atenciones.services.atencion_service.solicitudes_client.buscar_solicitudes_por_cliente_nombre",
        lambda nombre: [],
    )

    resp = api_client_coordinador.get(
        "/api/atenciones/", {"cliente_nombre": "NoExiste"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []
    assert data["count"] == 0
