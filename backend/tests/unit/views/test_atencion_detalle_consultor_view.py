"""
HU-05: Pruebas unitarias de AtencionDetalleView — rama CONSULTOR.

Verifica que la vista:
  - Retorna 200 con datos de contacto para consultores asignados (CA-1, CA-2)
  - Retorna 403 con el mensaje exacto para consultores no asignados (CA-3)
  - Retorna 200 con contacto_disponible=False cuando el módulo Clientes falla (CA-4)
  - Retorna 401 cuando faltan cabeceras de autenticación
  - No confunde rol CLIENTE con CONSULTOR
"""

import pytest
from unittest.mock import patch

from rest_framework.test import APIRequestFactory

from atenciones.dtos.output.atencion_detalle_consultor_dto import (
    MSG_CONTACTO_NO_DISPONIBLE,
    NO_REGISTRADO,
    AtencionDetalleConsultorDTO,
)
from atenciones.exceptions import AtencionDoesNotExist, AtencionServiceUnavailableError
from atenciones.exceptions.custom_exceptions import ConsultorNoAsignado
from atenciones.views.atencion_detalle_view import AtencionDetalleView

CONSULTOR_ID = "consultor-uuid-001"

factory = APIRequestFactory()


def _make_dto(**overrides) -> AtencionDetalleConsultorDTO:
    """Retorna un DTO de consultor con valores por defecto, aplicando overrides."""
    defaults = {
        "id": 1,
        "request_id": "sol-001",
        "solicitud_nombre": "Solicitud 001",
        "scheduled_date": None,
        "closing_date": None,
        "status": "AGENDADA",
        "diagnostico_inicial": None,
        "notas": [],
        "mensaje_bitacora": "Esta atención no tiene notas de seguimiento registradas.",
        "acciones_disponibles": {"editar": True, "finalizar": True, "cancelar": True},
        "contacto_nombre": "Ana García",
        "contacto_telefono": "3001234567",
        "contacto_correo": "ana@test.com",
        "contacto_disponible": True,
        "contacto_error_msg": None,
    }
    defaults.update(overrides)
    return AtencionDetalleConsultorDTO(**defaults)  # type: ignore


def _get(pk: int, user_id: str = CONSULTOR_ID, user_role: str = "CONSULTOR"):
    """Dispara GET /api/atenciones/{pk}/ con cabeceras de contexto de usuario."""
    request = factory.get(f"/api/atenciones/{pk}/")
    request.META["HTTP_X_USER_ID"] = user_id
    request.META["HTTP_X_USER_ROLE"] = user_role
    view = AtencionDetalleView.as_view()
    return view(request, pk=pk)


# ─── CA-1 y CA-2: consultor asignado recibe 200 con contacto ────────────────


@pytest.mark.unit
@patch(
    "atenciones.views.atencion_detalle_view.AtencionDetalleConsultorService.obtener_detalle_consultor"
)
def test_consultor_asignado_retorna_200_con_contacto(mock_service):
    """CA-1/CA-2: respuesta 200 con los tres campos de contacto."""
    mock_service.return_value = _make_dto()

    response = _get(pk=1)

    assert response.status_code == 200
    assert response.data["contacto_nombre"] == "Ana García"
    assert response.data["contacto_telefono"] == "3001234567"
    assert response.data["contacto_correo"] == "ana@test.com"
    assert response.data["contacto_disponible"] is True
    assert response.data["contacto_error_msg"] is None


# ─── CA-3: consultor no asignado recibe 403 con mensaje exacto ──────────────


@pytest.mark.unit
@patch(
    "atenciones.views.atencion_detalle_view.AtencionDetalleConsultorService.obtener_detalle_consultor"
)
def test_consultor_no_asignado_retorna_403_con_mensaje(mock_service):
    """CA-3: 403 con el mensaje exacto del criterio de aceptación."""
    mock_service.side_effect = ConsultorNoAsignado()

    response = _get(pk=1)

    assert response.status_code == 403
    assert (
        response.data["detail"]
        == "No tiene permisos para consultar el detalle de esta atención."
    )


# ─── CA-4: módulo Clientes no disponible retorna 200 con degradación ────────


@pytest.mark.unit
@patch(
    "atenciones.views.atencion_detalle_view.AtencionDetalleConsultorService.obtener_detalle_consultor"
)
def test_servicio_clientes_no_disponible_retorna_200_con_mensaje_degradacion(
    mock_service,
):
    """CA-4: 200 con contacto_disponible=False y el mensaje de degradación."""
    mock_service.return_value = _make_dto(
        contacto_disponible=False,
        contacto_error_msg=MSG_CONTACTO_NO_DISPONIBLE,
        contacto_nombre=NO_REGISTRADO,
        contacto_telefono=NO_REGISTRADO,
        contacto_correo=NO_REGISTRADO,
    )

    response = _get(pk=1)

    assert response.status_code == 200
    assert response.data["contacto_disponible"] is False
    assert response.data["contacto_error_msg"] == MSG_CONTACTO_NO_DISPONIBLE
    # Los campos de contacto deben ser "No registrado", no None ni ausentes (CA-5)
    assert response.data["contacto_nombre"] == NO_REGISTRADO
    assert response.data["contacto_telefono"] == NO_REGISTRADO
    assert response.data["contacto_correo"] == NO_REGISTRADO


# ─── Sin cabeceras → 401 ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_sin_cabeceras_retorna_401():
    """Sin X-User-Id ni X-User-Role la vista debe retornar 401."""
    request = factory.get("/api/atenciones/1/")
    view = AtencionDetalleView.as_view()
    response = view(request, pk=1)

    assert response.status_code == 401


# ─── Rol CLIENTE no accede a la rama CONSULTOR ───────────────────────────────


@pytest.mark.unit
def test_rol_cliente_retorna_403():
    """Un usuario con rol CLIENTE no debe acceder a la rama CONSULTOR ni a COORDINADOR."""
    response = _get(pk=1, user_role="CLIENTE")

    assert response.status_code == 403


# ─── Atención no encontrada ──────────────────────────────────────────────────


@pytest.mark.unit
@patch(
    "atenciones.views.atencion_detalle_view.AtencionDetalleConsultorService.obtener_detalle_consultor"
)
def test_atencion_inexistente_retorna_404(mock_service):
    """Si la atención no existe después de validar la asignación, se retorna 404."""
    mock_service.side_effect = AtencionDoesNotExist()

    response = _get(pk=9999)

    assert response.status_code == 404


# ─── Error de BD → 503 ───────────────────────────────────────────────────────


@pytest.mark.unit
@patch(
    "atenciones.views.atencion_detalle_view.AtencionDetalleConsultorService.obtener_detalle_consultor"
)
def test_error_de_bd_retorna_503(mock_service):
    """Si hay un error de BD, la vista retorna 503."""
    mock_service.side_effect = AtencionServiceUnavailableError()

    response = _get(pk=1)

    assert response.status_code == 503
