from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.db import models

from atenciones.constants import EstadoAtencion


class Atention(models.Model):
    # HU-02: request_id es UUID string del módulo de Solicitudes externo
    request_id: models.CharField[str, str] = models.CharField(
        max_length=64, db_index=True
    )
    status: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EstadoAtencion],
        default=EstadoAtencion.AGENDADA,
    )

    scheduled_date: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )
    closing_date: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )
    final_note: models.TextField[str | None, str | None] = models.TextField(
        null=True, blank=True
    )
    cancellation_reason: models.TextField[str | None, str | None] = models.TextField(
        null=True, blank=True
    )
    # HU-02: created_by es opcional mientras auth/RBAC no esté activo
    created_by: models.CharField[str | None, str | None] = models.CharField(
        max_length=128, null=True, blank=True
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True
    )

    if TYPE_CHECKING:
        from .atention_cosultor import AtentionConsultant

        consultants_rel: models.Manager[AtentionConsultant]

    class Meta:
        db_table = "atention"
        indexes = [
            models.Index(fields=["status", "scheduled_date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Atention({self.pk}, {self.status})"
