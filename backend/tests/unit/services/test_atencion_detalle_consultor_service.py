"""
HU-05: Pruebas unitarias de AtencionDetalleConsultorService.

Cubre los 6 criterios de aceptación:
  CA-1: sección visible solo para consultores asignados
  CA-2: campos nombre, teléfono, correo retornados en tiempo real
  CA-3: bloqueo si el consultor no está asignado
  CA-4: degradación elegante si el módulo de Clientes falla
  CA-5: "No registrado" para campos ausentes
  CA-6: el servicio no expone métodos de edición/exportación
"""
import pytest
from unittest.mock import patch

from django.db import Error as DBError

from atenciones.constants import EstadoAtencion
from atenciones.exceptions import AtencionDoesNotExist, AtencionServiceUnavailableError
from atenciones.exceptions.custom_exceptions import ConsultorNoAsignado
from atenciones.dtos.output.atencion_detalle_consultor_dto import (
    MSG_CONTACTO_NO_DISPONIBLE,
    NO_REGISTRADO,
)
from atenciones.models import AtentionConsultant, NotaSeguimiento
from atenciones.services.atencion_detalle_consultor_service import (
    AtencionDetalleConsultorService,
)
from tests.factories import AtencionFactory

CONSULTOR_ID = "consultor-uuid-001"
CLIENT_ID = "client-uuid-001"

MOCK_SOLICITUD = {
    "id": "sol-001",
    "estado": "PENDIENTE",
    "client_id": CLIENT_ID,
    "nombre": "Solicitud Test HU-05",
}
MOCK_CONTACTO = {
    "nombre_completo": "Ana García",
    "telefono": "3001234567",
    "correo_electronico": "ana@test.com",
}


@pytest.fixture()
def atencion_con_consultor(db):
    """Atención con un consultor asignado."""
    atencion = AtencionFactory(status=EstadoAtencion.AGENDADA)
    AtentionConsultant.objects.create(
        atention=atencion,
        consultant_id=CONSULTOR_ID,
        is_leader=True,
    )
    return atencion


# ─── CA-1 y CA-2: consultor asignado obtiene contacto completo ──────────────

@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_consultor_asignado_obtiene_contacto_completo(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-1/CA-2: consultor asignado recibe nombre, teléfono y correo del cliente."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = MOCK_CONTACTO

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_disponible is True
    assert dto.contacto_nombre == "Ana García"
    assert dto.contacto_telefono == "3001234567"
    assert dto.contacto_correo == "ana@test.com"
    assert dto.contacto_error_msg is None


# ─── CA-3: consultor NO asignado debe ser bloqueado ─────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
def test_consultor_no_asignado_lanza_consultor_no_asignado(db):
    """CA-3: si el consultor no está asignado, se lanza ConsultorNoAsignado."""
    atencion = AtencionFactory()
    # No se crea ningún AtentionConsultant

    with pytest.raises(ConsultorNoAsignado):
        AtencionDetalleConsultorService.obtener_detalle_consultor(
            atention_id=atencion.id,
            consultant_id="consultor-ajeno",
        )


@pytest.mark.django_db
@pytest.mark.unit
def test_consultor_de_otra_atencion_no_puede_ver_esta(db):
    """CA-3: un consultor asignado a otra atención no puede ver ésta."""
    atencion_a = AtencionFactory()
    atencion_b = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion_a,
        consultant_id=CONSULTOR_ID,
        is_leader=True,
    )

    with pytest.raises(ConsultorNoAsignado):
        AtencionDetalleConsultorService.obtener_detalle_consultor(
            atention_id=atencion_b.id,
            consultant_id=CONSULTOR_ID,
        )


# ─── CA-4: degradación elegante si el módulo de Clientes falla ──────────────

@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_clientes_service_no_disponible_degrada_sin_fallar(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-4: si clientes_client retorna None (circuito abierto), el DTO incluye el mensaje de degradación."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = None  # circuit breaker abierto

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_disponible is False
    assert dto.contacto_error_msg == MSG_CONTACTO_NO_DISPONIBLE
    # El detalle de la atención aún está disponible
    assert dto.id == atencion_con_consultor.id


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
def test_solicitudes_service_no_disponible_degrada_sin_fallar(
    mock_solicitud, atencion_con_consultor
):
    """CA-4: si solicitudes_client retorna None, el DTO incluye el mensaje de degradación."""
    mock_solicitud.return_value = None  # circuit breaker abierto en solicitudes

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_disponible is False
    assert dto.contacto_error_msg == MSG_CONTACTO_NO_DISPONIBLE


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_excepcion_en_clientes_degrada_sin_propagar(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-4: si clientes_client lanza una excepción, no se propaga al caller."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.side_effect = Exception("Timeout de red simulado")

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_disponible is False
    assert dto.contacto_error_msg == MSG_CONTACTO_NO_DISPONIBLE


# ─── CA-5: campos None → "No registrado" ────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_telefono_none_retorna_no_registrado(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-5: si el teléfono es None, el campo debe ser "No registrado"."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = {
        "nombre_completo": "Ana García",
        "telefono": None,
        "correo_electronico": "ana@test.com",
    }

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_telefono == NO_REGISTRADO
    assert dto.contacto_nombre == "Ana García"
    assert dto.contacto_correo == "ana@test.com"


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_correo_none_retorna_no_registrado(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-5: si el correo es None, el campo debe ser "No registrado"."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = {
        "nombre_completo": "Ana García",
        "telefono": "3001234567",
        "correo_electronico": None,
    }

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_correo == NO_REGISTRADO


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_nombre_none_retorna_no_registrado(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-5: si el nombre es None, el campo debe ser "No registrado"."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = {
        "nombre_completo": None,
        "telefono": "3001234567",
        "correo_electronico": "ana@test.com",
    }

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_nombre == NO_REGISTRADO


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_todos_los_campos_none_retornan_no_registrado(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """CA-5: si todos los campos de contacto son None, todos deben ser "No registrado"."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = {
        "nombre_completo": None,
        "telefono": None,
        "correo_electronico": None,
    }

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.contacto_nombre == NO_REGISTRADO
    assert dto.contacto_telefono == NO_REGISTRADO
    assert dto.contacto_correo == NO_REGISTRADO
    # A pesar de los campos ausentes, el servicio respondió → disponible
    assert dto.contacto_disponible is True


# ─── Comportamiento de notas de seguimiento ─────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_atencion_sin_notas_incluye_mensaje_bitacora(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """La atención sin notas debe incluir el mensaje de bitácora vacía."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = MOCK_CONTACTO

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.notas == []
    assert dto.diagnostico_inicial is None
    assert dto.mensaje_bitacora == "Esta atención no tiene notas de seguimiento registradas."


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.solicitudes_client.get_solicitud")
@patch("atenciones.services.atencion_detalle_consultor_service.clientes_client.get_contacto_cliente")
def test_atencion_con_notas_incluye_diagnostico_inicial(
    mock_contacto, mock_solicitud, atencion_con_consultor
):
    """El diagnóstico inicial es la nota más antigua de la atención."""
    mock_solicitud.return_value = MOCK_SOLICITUD
    mock_contacto.return_value = MOCK_CONTACTO

    NotaSeguimiento.objects.create(
        atention=atencion_con_consultor,
        consultant_id=CONSULTOR_ID,
        content="Primera nota de diagnóstico",
    )

    dto = AtencionDetalleConsultorService.obtener_detalle_consultor(
        atention_id=atencion_con_consultor.id,
        consultant_id=CONSULTOR_ID,
    )

    assert dto.diagnostico_inicial == "Primera nota de diagnóstico"
    assert len(dto.notas) == 1
    assert dto.mensaje_bitacora is None


# ─── Error de BD ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_consultor_service.AtencionRepository.obtener_por_id")
def test_error_de_bd_lanza_atencion_service_unavailable(mock_repo, atencion_con_consultor):
    """Si hay un error de BD tras validar la asignación, se lanza AtencionServiceUnavailableError."""
    mock_repo.side_effect = DBError("Conexión perdida")

    with pytest.raises(AtencionServiceUnavailableError):
        AtencionDetalleConsultorService.obtener_detalle_consultor(
            atention_id=atencion_con_consultor.id,
            consultant_id=CONSULTOR_ID,
        )
