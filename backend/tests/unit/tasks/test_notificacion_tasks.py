from unittest.mock import patch

import pytest

from atenciones.tasks.notificacion_tasks import (
    enviar_email_anulacion,
    enviar_email_cliente,
    enviar_notificacion_programacion,
    registrar_heartbeat_beat,
)


@pytest.mark.unit
def test_tareas_de_notificacion_registran_log():
    with patch("atenciones.tasks.notificacion_tasks.logger") as logger:
        enviar_notificacion_programacion.run(1)
        enviar_email_cliente.run(2)
        enviar_email_anulacion.run(3)

    assert logger.info.call_count == 3


@pytest.mark.unit
def test_registrar_heartbeat_beat_guarda_timestamp():
    with patch("atenciones.tasks.notificacion_tasks.time.time", return_value=123.45):
        with patch("atenciones.tasks.notificacion_tasks.cache") as cache:
            registrar_heartbeat_beat()

    cache.set.assert_called_once_with(
        "celery_beat_last_heartbeat",
        123.45,
        timeout=120,
    )
