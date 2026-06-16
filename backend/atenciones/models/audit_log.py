# CONCERN-04: AuditLog append-only con particionado mensual (anotación)
from __future__ import annotations

from datetime import datetime

from django.db import models


class AuditLog(models.Model):
    operation: models.CharField[str, str] = models.CharField(max_length=64)
    actor_id: models.IntegerField[int, int] = models.IntegerField()
    actor_role: models.CharField[str, str] = models.CharField(max_length=32)
    atention_id: models.IntegerField[int | None, int | None] = models.IntegerField(
        null=True, blank=True
    )
    payload_hash_sha256: models.CharField[str, str] = models.CharField(max_length=64)
    jwt_subject: models.CharField[str, str] = models.CharField(max_length=255)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "audit_log"
        # partitioned_by_month: implementado a nivel operativo (archival + índices por fecha)
        indexes = [models.Index(fields=["created_at"])]
