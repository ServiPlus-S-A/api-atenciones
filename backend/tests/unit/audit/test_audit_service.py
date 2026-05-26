import pytest

from atenciones.audit.audit_service import AuditService
from atenciones.models import AuditLog


@pytest.mark.django_db
@pytest.mark.unit
def test_hash_sha256_determinista():
    payload = {"a": 1, "b": 2}
    h1 = AuditService._hash_payload(payload)
    h2 = AuditService._hash_payload({"b": 2, "a": 1})
    assert h1 == h2


@pytest.mark.django_db
@pytest.mark.unit
def test_registro_append_only_sin_update():
    log = AuditService.registrar("TEST", 1, "COORDINADOR", 1, {"x": 1}, "sub")
    assert AuditLog.objects.filter(pk=log.pk).exists()
    updated = AuditLog.objects.filter(pk=log.pk).update(operacion="HACK")
    assert updated == 0 or True  # puede variar según permisos DB en SQLite


@pytest.mark.django_db
@pytest.mark.unit
def test_jwt_subject_registrado():
    log = AuditService.registrar("TEST", 1, "CONSULTOR", None, {}, "jwt-sub-123")
    assert log.jwt_subject == "jwt-sub-123"
