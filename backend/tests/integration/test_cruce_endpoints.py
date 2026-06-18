import pytest
from datetime import datetime, timedelta, timezone
from rest_framework import status
from atenciones.models import AtentionConsultant
from tests.factories.atencion_factory import AtencionFactory


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_verificar_cruce_sin_cruce(api_client_consultor):
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    response = api_client_consultor.get(
        "/api/atenciones/verificar-cruce/",
        {
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat(),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"cruce": False}


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_verificar_cruce_con_cruce_valido(api_client_consultor):
    user = api_client_consultor.test_user
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    # Existing scheduled attention for user
    atencion = AtencionFactory(scheduled_date=inicio, closing_date=fin)
    AtentionConsultant.objects.create(atention=atencion, consultant_id=user.id)

    # Query overlapping but 30-min block aligned: 10:30 to 11:30
    query_inicio = inicio + timedelta(minutes=30)
    query_fin = fin + timedelta(minutes=30)

    response = api_client_consultor.get(
        "/api/atenciones/verificar-cruce/",
        {
            "fecha_inicio": query_inicio.isoformat(),
            "fecha_fin": query_fin.isoformat(),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cruce"] is True
    assert (
        "Ya tienes una atención programada en este horario. Por favor selecciona otro."
        in data["mensaje"]
    )
    assert len(data["cruces"]) == 1
    assert data["cruces"][0]["consultor_id"] == str(user.id)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_consultor_asignado_puede_programar(api_client_consultor):
    user = api_client_consultor.test_user
    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )

    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion.pk}/programar/",
        {"fecha_programada": inicio.isoformat(), "fecha_fin": fin.isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["scheduled_date"] is not None


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_consultor_no_asignado_no_puede_programar(api_client_consultor):
    atencion = AtencionFactory()

    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion.pk}/programar/",
        {"fecha_programada": inicio.isoformat(), "fecha_fin": fin.isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_coordinador_puede_programar_cualquiera(api_client_coordinador):
    atencion = AtencionFactory()

    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    response = api_client_coordinador.patch(
        f"/api/atenciones/{atencion.pk}/programar/",
        {"fecha_programada": inicio.isoformat(), "fecha_fin": fin.isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_programar_cruce_retorna_409_con_detalles(api_client_consultor):
    user = api_client_consultor.test_user

    # 1. Create an attention that we want to program
    atencion_nueva = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion_nueva, consultant_id=user.id, is_leader=True
    )

    # 2. Create an already existing scheduled attention that overlaps
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)

    atencion_ocupada = AtencionFactory(scheduled_date=inicio, closing_date=fin)
    AtentionConsultant.objects.create(atention=atencion_ocupada, consultant_id=user.id)

    # 3. Try to program the new one in the overlapping block (e.g. 10:30 to 11:30)
    query_inicio = inicio + timedelta(minutes=30)
    query_fin = fin + timedelta(minutes=30)

    response = api_client_consultor.patch(
        f"/api/atenciones/{atencion_nueva.pk}/programar/",
        {
            "fecha_programada": query_inicio.isoformat(),
            "fecha_fin": query_fin.isoformat(),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data["error"] == "cruce_horario"
    assert (
        "Ya tienes una atención programada en este horario. Por favor selecciona otro."
        in data["message"]
    )
    assert "cruces" in data
    assert len(data["cruces"]) == 1
    assert data["cruces"][0]["consultor_id"] == str(user.id)
