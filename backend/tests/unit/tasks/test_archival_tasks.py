import pytest

from atenciones.tasks.archival_tasks import archival_audit_log_mensual


@pytest.mark.unit
def test_archival_audit_log_mensual_calls_command(monkeypatch):
    called = {"count": 0}

    def fake_call_command(name):
        if name == "archival_audit_log":
            called["count"] += 1

    monkeypatch.setattr("atenciones.tasks.archival_tasks.call_command", fake_call_command)

    archival_audit_log_mensual()

    assert called["count"] == 1
