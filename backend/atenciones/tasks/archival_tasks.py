from celery import shared_task
from django.core.management import call_command


@shared_task
def archival_audit_log_mensual():
    """CONCERN-03: delega al management command archival_audit_log."""
    call_command("archival_audit_log")
