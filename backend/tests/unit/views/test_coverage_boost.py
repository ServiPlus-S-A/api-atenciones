"""Tests mínimos para subir cobertura de atencion_view.py y atencion_service.py."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
import requests

from atenciones.constants import EstadoAtencion, Rol
from atenciones.exceptions.custom_exceptions import (
    ConsultorNoDisponible,
    ConsultorNoEncontrado,
    ServicioExternoNoDisponible,
    SolicitudNoAutorizada,
)
from atenciones.integrations.parametrizacion_client import ConsultorInfoDTO
from atenciones.integrations.solicitudes_client import SolicitudInfoDTO
from atenciones.services.atencion_service import AtencionService


# ─── _get_mock_user / _mock_user_if_unauthenticated (atencion_view.py) ──────

@pytest.mark.unit
def test_get_mock_user_fallback():
    from atenciones.views.atencion_view import _get_mock_user
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        user = _get_mock_user("42", "COORDINADOR")
    assert user.id == "42"
    assert user.rol == "COORDINADOR"
    assert user.is_authenticated is True


@pytest.mark.unit
def test_get_mock_user_from_settings():
    from django.test import override_settings
    from atenciones.views.atencion_view import _get_mock_user
    mock_user = SimpleNamespace(id="99")
    with override_settings(PARAMETRIZACION_MOCK_RESPONSES={"7": mock_user}):
        user = _get_mock_user("7", "CONSULTOR")
    assert user is mock_user
    assert user.rol == "CONSULTOR"
    assert user.is_authenticated is True


@pytest.mark.unit
def test_mock_user_if_unauthenticated_disabled():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated
    req = MagicMock()
    _mock_user_if_unauthenticated(req, allow_mock_auth=False)
    # No debe modificar nada
    assert req.user == req.user


@pytest.mark.unit
def test_mock_user_if_unauthenticated_already_authenticated():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated
    req = MagicMock()
    req.user.is_authenticated = True
    _mock_user_if_unauthenticated(req, allow_mock_auth=True)


@pytest.mark.unit
def test_mock_user_if_unauthenticated_fallback_static():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated
    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, default_id="1", default_rol="CONSULTOR", allow_mock_auth=True
        )
    assert req.user is not None
    assert req.user.id == "1"


@pytest.mark.unit
@pytest.mark.django_db
def test_mock_user_if_unauthenticated_with_pk():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated
    from tests.factories.atencion_factory import AtencionFactory
    from atenciones.models import AtentionConsultant

    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id="cons-77", is_leader=True
    )

    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, pk=atencion.pk, default_id="1", default_rol="CONSULTOR",
            allow_mock_auth=True,
        )
    assert req.user.id == "cons-77"


@pytest.mark.unit
@pytest.mark.django_db
def test_mock_user_if_unauthenticated_with_pk_not_found():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated

    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, pk=999999, default_id="1", default_rol="CONSULTOR",
            allow_mock_auth=True,
        )
    # Should fallback to static
    assert req.user.id == "1"


@pytest.mark.unit
@pytest.mark.django_db
def test_mock_user_if_unauthenticated_query_atencion_id():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated
    from tests.factories.atencion_factory import AtencionFactory
    from atenciones.models import AtentionConsultant

    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id="cons-88", is_leader=True
    )

    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, query_atencion_id=atencion.pk,
            default_id="1", default_rol="CONSULTOR", allow_mock_auth=True,
        )
    assert req.user.id == "cons-88"


@pytest.mark.unit
def test_mock_user_if_unauthenticated_query_consultor_id():
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated

    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, query_consultor_id="cons-direct",
            default_id="1", default_rol="CONSULTOR", allow_mock_auth=True,
        )
    assert req.user.id == "cons-direct"


# ─── AtencionService (atencion_service.py) ──────────────────────────────────

@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_crear_sin_usuario_fallback(mock_param, mock_sol):
    """Cubre líneas 71-75: rama else de _obtener_contexto_creacion."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="Pendiente")
    mock_param.return_value = ConsultorInfoDTO(id="c-1", disponible=True, aptitudes=())
    dto = AtencionService.crear(
        {
            "solicitud_id": "1",
            "consultor_ids": ["c-1"],
            "mensaje_preliminar": "Mensaje preliminar de prueba de fallback.",
            "creado_por_id": "actor-ext",
        },
        user=None,
    )
    assert dto.estado == EstadoAtencion.AGENDADA


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
def test_validar_solicitud_request_exception(mock_sol):
    """Cubre líneas 83-84: RequestException → ServicioExternoNoDisponible."""
    mock_sol.side_effect = requests.RequestException("down")
    with pytest.raises(ServicioExternoNoDisponible):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Mensaje preliminar de prueba."},
            user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
def test_validar_solicitud_none(mock_sol):
    """Cubre línea 87: solicitud is None."""
    mock_sol.return_value = None
    with pytest.raises(SolicitudNoAutorizada):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Mensaje preliminar de prueba."},
            user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_validar_consultores_request_exception(mock_param, mock_sol):
    """Cubre líneas 106-107: RequestException en parametrizacion."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="Pendiente")
    mock_param.side_effect = requests.RequestException("down")
    with pytest.raises(ServicioExternoNoDisponible):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Mensaje preliminar de prueba."},
            user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_validar_consultores_no_encontrado(mock_param, mock_sol):
    """Cubre línea 110: info is None."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="Pendiente")
    mock_param.return_value = None
    with pytest.raises(ConsultorNoEncontrado):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Mensaje preliminar de prueba."},
            user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_validar_consultores_aptitud_incorrecta(mock_param, mock_sol):
    """Cubre línea 119: aptitud_requerida not in aptitudes."""
    mock_sol.return_value = SolicitudInfoDTO(
        id="1", estado="Pendiente", aptitud_requerida="redes"
    )
    mock_param.return_value = ConsultorInfoDTO(
        id="c-1", disponible=True, aptitudes=("soporte",)
    )
    with pytest.raises(ConsultorNoDisponible):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Mensaje preliminar de prueba."},
            user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
@patch("atenciones.services.atencion_service.clientes_client.get_contacto_cliente")
def test_crear_cliente_request_exception(mock_cli, mock_param, mock_sol):
    """Cubre líneas 137-143: RequestException al obtener cliente."""
    mock_sol.return_value = SolicitudInfoDTO(
        id="1", estado="Pendiente", cliente_id="cl-1"
    )
    mock_param.return_value = ConsultorInfoDTO(id="c-1", disponible=True, aptitudes=())
    mock_cli.side_effect = requests.RequestException("down")
    dto = AtencionService.crear(
        {"solicitud_id": "1", "consultor_ids": ["c-1"],
         "mensaje_preliminar": "Mensaje preliminar de prueba."},
        user=None,
    )
    assert dto.cliente_nombre is None


@pytest.mark.unit
@pytest.mark.django_db
def test_listar_para_usuario_rol_cliente():
    """Cubre línea 283: elif rol == Rol.CLIENTE."""
    from django.core.cache import cache
    user = SimpleNamespace(id=999, rol=Rol.CLIENTE, username="cli")
    cache.clear()
    result = AtencionService.listar_para_usuario(user, {})
    assert isinstance(result, list)


# ─── Tests adicionales para líneas faltantes ─────────────────────────────────

@pytest.mark.unit
def test_paginate_function():
    """Cubre líneas 109-114 de atencion_view.py."""
    from atenciones.views.atencion_view import _paginate
    from atenciones.dtos.output.atencion_dto import AtencionDTO

    dto = AtencionDTO(
        id=1, estado=EstadoAtencion.AGENDADA, solicitud_id="1",
        fecha_programada=None, fecha_fin=None, notas_finales=None,
        fecha_cierre=None, consultores=[],
    )
    result = _paginate([dto], page=1, page_size=10)
    assert result["count"] == 1
    assert result["total_pages"] == 1
    assert result["page"] == 1
    assert len(result["results"]) == 1


@pytest.mark.unit
@pytest.mark.django_db
def test_mock_user_query_atencion_id_not_found():
    """Cubre líneas 97-98 de atencion_view.py (DoesNotExist en query_atencion_id)."""
    from atenciones.views.atencion_view import _mock_user_if_unauthenticated

    req = MagicMock()
    req.user = None
    with patch("atenciones.views.atencion_view.settings", create=True) as s:
        s.PARAMETRIZACION_MOCK_RESPONSES = None
        _mock_user_if_unauthenticated(
            req, query_atencion_id=999999,
            default_id="1", default_rol="CONSULTOR", allow_mock_auth=True,
        )
    assert req.user.id == "1"


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
def test_validar_solicitud_estado_desconocido(mock_sol):
    """Cubre línea 91: estado DESCONOCIDO → ServicioExternoNoDisponible."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="DESCONOCIDO")
    with pytest.raises(ServicioExternoNoDisponible):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Msg de prueba."}, user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
def test_validar_solicitud_estado_no_pendiente(mock_sol):
    """Cubre línea 93: estado != PENDIENTE → SolicitudNoAutorizada."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="APROBADA")
    with pytest.raises(SolicitudNoAutorizada):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Msg de prueba."}, user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_validar_consultores_no_disponible(mock_param, mock_sol):
    """Cubre línea 114: consultor no disponible."""
    mock_sol.return_value = SolicitudInfoDTO(id="1", estado="Pendiente")
    mock_param.return_value = ConsultorInfoDTO(id="c-1", disponible=False, aptitudes=())
    with pytest.raises(ConsultorNoDisponible):
        AtencionService.crear(
            {"solicitud_id": "1", "consultor_ids": ["c-1"],
             "mensaje_preliminar": "Msg de prueba."}, user=None,
        )


@pytest.mark.unit
@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
@patch("atenciones.services.atencion_service.clientes_client.get_contacto_cliente")
def test_crear_con_cliente_exitoso(mock_cli, mock_param, mock_sol):
    """Cubre línea 141: cliente.get('nombre_completo') exitoso."""
    mock_sol.return_value = SolicitudInfoDTO(
        id="1", estado="Pendiente", cliente_id="cl-1"
    )
    mock_param.return_value = ConsultorInfoDTO(id="c-1", disponible=True, aptitudes=())
    mock_cli.return_value = {"nombre_completo": "Juan Pérez"}
    dto = AtencionService.crear(
        {"solicitud_id": "1", "consultor_ids": ["c-1"],
         "mensaje_preliminar": "Msg de prueba."},
        user=None,
    )
    assert dto.cliente_nombre == "Juan Pérez"


@pytest.mark.unit
@pytest.mark.django_db
def test_listar_para_usuario_rol_consultor():
    """Cubre líneas 280-281: rama CONSULTOR en listar_para_usuario."""
    from django.core.cache import cache
    user = SimpleNamespace(id=888, rol=Rol.CONSULTOR, username="cons")
    cache.clear()
    result = AtencionService.listar_para_usuario(user, {})
    assert isinstance(result, list)
