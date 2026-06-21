# CONCERN-04: AuditLog append-only con particionado mensual (anotación)
from __future__ import annotations

from datetime import datetime

from django.db import models


class AuditLog(models.Model):
    operation: models.CharField[str, str] = models.CharField(max_length=64)
    # HU-02: actor_id es UUID/string mientras auth no esté activa
    actor_id: models.CharField[str, str] = models.CharField(max_length=128)
    actor_role: models.CharField[str, str] = models.CharField(max_length=32)
    atention_id: models.BigIntegerField[int | None, int | None] = (
        models.BigIntegerField(null=True, blank=True)
    )
    payload_hash_sha256: models.CharField[str, str] = models.CharField(max_length=64)
    # HU-02: nullable mientras JWT/auth no esté activo
    jwt_subject: models.CharField[str | None, str | None] = models.CharField(
        max_length=255, null=True, blank=True
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "audit_log"
        # partitioned_by_month: implementado a nivel operativo (archival + índices por fecha)
        indexes = [models.Index(fields=["created_at"])]
