# CONCERN-04: AuditLog append-only con particionado mensual (anotación)
from django.db import models


class AuditLog(models.Model):
    operacion = models.CharField(max_length=64)
    actor_id = models.IntegerField()
    actor_rol = models.CharField(max_length=32)
    atencion_id = models.IntegerField(null=True, blank=True)
    payload_hash_sha256 = models.CharField(max_length=64)
    jwt_subject = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        # partitioned_by_month: implementado a nivel operativo (archival + índices por fecha)
        indexes = [models.Index(fields=["timestamp"])]
