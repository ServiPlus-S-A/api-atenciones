import hashlib
import json
import logging

import pytest

from atenciones.models import AuditLog
from atenciones.security.secure_logger import SecureLogger


@pytest.mark.django_db
@pytest.mark.unit
def test_registrar_crea_audit_log_y_hash():
    payload = {"b": 2, "a": 1}
    SecureLogger.registrar(
        operation="TEST",
        actor_id=7,
        actor_role="COORDINADOR",
        resource_id=123,
        ip_origin="127.0.0.1",
        jwt_subject="jwt-sub",
        payload=payload,
    )

    log = AuditLog.objects.get(operation="TEST", actor_id=7)
    canonical = json.dumps(payload, sort_keys=True, default=str)
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    assert log.payload_hash_sha256 == expected_hash
    assert log.actor_role == "COORDINADOR"
    assert log.atention_id == 123
    assert log.jwt_subject == "jwt-sub"


@pytest.mark.unit
def test_registrar_fallo_logs_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="atenciones.secure"):
        SecureLogger.registrar_fallo(
            operation="EXCEPTION",
            actor_id=None,
            detail="boom",
            context={"path": "/api/atenciones/"},
        )

    assert "failure operation=EXCEPTION" in caplog.text
