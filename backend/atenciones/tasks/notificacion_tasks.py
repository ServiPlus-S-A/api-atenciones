import logging
import time

from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger("atenciones.tasks")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_notificacion_programacion(self, atencion_id: int):
    try:
        logger.info("Notificación programación atención %s", atencion_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_cliente(self, atencion_id: int):
    try:
        logger.info("Email cliente atención %s", atencion_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_anulacion(self, atencion_id: int):
    try:
        logger.info("Email anulación atención %s", atencion_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries)


@shared_task
def registrar_heartbeat_beat():
    cache.set("celery_beat_last_heartbeat", time.time(), timeout=120)
