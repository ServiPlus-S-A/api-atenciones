import pytest

from atenciones.models import AuditLog
from atenciones.security.secure_logger import SecureLogger


@pytest.mark.django_db
def test_registrar_crea_audit_log():
    SecureLogger.registrar(
        operation="TEST",
        actor_id=1,
        actor_role="COORDINADOR",
        resource_id=99,
        ip_origin="127.0.0.1",
        jwt_subject="user_test",
        payload={"clave": "valor"},
    )
    log = AuditLog.objects.get(operation="TEST")
    assert log.actor_id == "1"
    assert log.atention_id == 99
    assert len(log.payload_hash_sha256) == 64


@pytest.mark.unit
def test_registrar_fallo_no_lanza():
    SecureLogger.registrar_fallo(
        operation="exception",
        actor_id=1,
        detail="fallo de prueba",
        context={},
    )
