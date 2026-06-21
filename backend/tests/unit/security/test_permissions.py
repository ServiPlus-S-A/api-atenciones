import pytest
from rest_framework.test import APIRequestFactory


from atenciones.models import AtentionConsultant
from atenciones.security.permissions import (
    IsCliente,
    IsConsultor,
    IsCoordinador,
    IsOwnerConsultorOrCoordinador,
)
from tests.factories.atencion_factory import AtencionFactory


def _request_with_user(user):
    request = APIRequestFactory().get("/")
    request.user = user
    return request


@pytest.mark.django_db
def test_is_coordinador(api_client_coordinador):
    perm = IsCoordinador()
    assert perm.has_permission(
        _request_with_user(api_client_coordinador.test_user), None
    )


@pytest.mark.django_db
def test_is_consultor(api_client_consultor):
    perm = IsConsultor()
    assert perm.has_permission(_request_with_user(api_client_consultor.test_user), None)


@pytest.mark.django_db
def test_is_cliente(api_client_cliente):
    perm = IsCliente()
    assert perm.has_permission(_request_with_user(api_client_cliente.test_user), None)


@pytest.mark.django_db
def test_owner_consultor_asignado(api_client_consultor):
    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    perm = IsOwnerConsultorOrCoordinador()
    assert perm.has_object_permission(_request_with_user(user), None, atencion)


@pytest.mark.django_db
def test_owner_consultor_no_asignado(api_client_consultor):
    atencion = AtencionFactory()
    perm = IsOwnerConsultorOrCoordinador()
    assert not perm.has_object_permission(
        _request_with_user(api_client_consultor.test_user),
        None,
        atencion,
    )


@pytest.mark.django_db
def test_owner_coordinador_siempre(api_client_coordinador):
    atencion = AtencionFactory()
    perm = IsOwnerConsultorOrCoordinador()
    assert perm.has_object_permission(
        _request_with_user(api_client_coordinador.test_user), None, atencion
    )
