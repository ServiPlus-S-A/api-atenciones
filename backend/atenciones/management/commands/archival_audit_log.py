import csv
import gzip
import io
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from atenciones.models import AuditLog


class Command(BaseCommand):
    """CONCERN-03: exporta audit_log > 6 meses a CSV+gzip; luego DELETE."""

    help = "Archiva registros de audit_log antiguos a Supabase Storage."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=180)
        qs = AuditLog.objects.filter(timestamp__lt=cutoff)
        count = qs.count()
        if count == 0:
            self.stdout.write("No hay registros para archivar.")
            return

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "operacion", "actor_id", "actor_rol", "atencion_id", "payload_hash_sha256", "jwt_subject", "timestamp"],
        )
        for log in qs.iterator():
            writer.writerow(
                [
                    log.id,
                    log.operacion,
                    log.actor_id,
                    log.actor_rol,
                    log.atencion_id,
                    log.payload_hash_sha256,
                    log.jwt_subject,
                    log.timestamp.isoformat(),
                ],
            )

        compressed = gzip.compress(buffer.getvalue().encode("utf-8"))
        filename = f"audit_log_{cutoff.strftime('%Y%m')}.csv.gz"
        self._upload_to_supabase(filename, compressed)
        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Archivados y eliminados {deleted} registros → {filename}"))

    def _upload_to_supabase(self, filename: str, data: bytes) -> None:
        if not settings.SUPABASE_URL:
            self.stdout.write(self.style.WARNING(f"Supabase no configurado; archivo local simulado: {filename}"))
            return
        import requests

        url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{filename}"
        requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/gzip",
            },
            data=data,
            timeout=30,
        )
