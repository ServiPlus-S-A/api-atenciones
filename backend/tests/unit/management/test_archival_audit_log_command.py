import io
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import override_settings

from atenciones.management.commands.archival_audit_log import Command
from atenciones.models import AuditLog


class _FakeQS:
    def __init__(self, items):
        self._items = items

    def count(self):
        return len(self._items)

    def iterator(self):
        return iter(self._items)

    def delete(self):
        return len(self._items), {}


@pytest.mark.unit
def test_archival_audit_log_no_records(monkeypatch):
    monkeypatch.setattr(AuditLog.objects, "filter", lambda *args, **kwargs: _FakeQS([]))

    out = io.StringIO()
    call_command("archival_audit_log", stdout=out)

    assert "No hay registros para archivar" in out.getvalue()


@pytest.mark.unit
def test_archival_audit_log_archives_and_deletes(monkeypatch):
    fake_log = SimpleNamespace(
        id=1,
        operacion="TEST",
        actor_id=10,
        actor_rol="COORDINADOR",
        atencion_id=99,
        payload_hash_sha256="hash",
        jwt_subject="jwt",
        timestamp=__import__("datetime").datetime(2024, 1, 1, 12, 0, 0),
    )
    monkeypatch.setattr(AuditLog.objects, "filter", lambda *args, **kwargs: _FakeQS([fake_log]))

    uploaded = {}

    def fake_upload(self, filename, data):
        uploaded["filename"] = filename
        uploaded["data"] = data

    monkeypatch.setattr(Command, "_upload_to_supabase", fake_upload)

    out = io.StringIO()
    call_command("archival_audit_log", stdout=out)

    assert "Archivados y eliminados 1 registros" in out.getvalue()
    assert uploaded["filename"].startswith("audit_log_")
    assert uploaded["data"]


@pytest.mark.unit
def test_upload_to_supabase_without_url_writes_warning():
    cmd = Command()
    cmd.stdout = io.StringIO()

    with override_settings(SUPABASE_URL=""):
        cmd._upload_to_supabase("file.gz", b"data")

    assert "Supabase no configurado" in cmd.stdout.getvalue()


@pytest.mark.unit
def test_upload_to_supabase_sends_request(monkeypatch):
    cmd = Command()
    cmd.stdout = io.StringIO()

    with override_settings(
        SUPABASE_URL="https://example.com",
        SUPABASE_STORAGE_BUCKET="bucket",
        SUPABASE_SERVICE_KEY="service-key",
    ):
        import requests

        captured = {}

        def fake_post(url, headers, data, timeout):
            captured["url"] = url
            captured["headers"] = headers
            captured["data"] = data
            captured["timeout"] = timeout

        monkeypatch.setattr(requests, "post", fake_post)

        cmd._upload_to_supabase("file.gz", b"data")

    assert captured["url"].endswith("/storage/v1/object/bucket/file.gz")
    assert captured["headers"]["Authorization"] == "Bearer service-key"
    assert captured["headers"]["Content-Type"] == "application/gzip"
    assert captured["data"] == b"data"
