import os
from dotenv import load_dotenv
load_dotenv()

from celery import Celery  # noqa: E402
from celery.schedules import crontab  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Beat schedule: archival_audit_log — CONCERN-03 (día 1 de cada mes, 02:00 UTC)
app.conf.beat_schedule = {
    "archival-audit-log-mensual": {
        "task": "atenciones.tasks.archival_tasks.archival_audit_log_mensual",
        "schedule": crontab(day_of_month=1, hour=2, minute=0),
    },
}
