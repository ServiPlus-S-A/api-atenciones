from __future__ import annotations

from datetime import datetime

from django.db import models

from .atention import Atention


class MonitoringNote(models.Model):
    atention: models.ForeignKey[Atention, Atention] = models.ForeignKey(
        Atention,
        on_delete=models.CASCADE,
        related_name="notes",
        db_column="atention_fk",
    )
    # HU-02: consultant_id es UUID string del módulo de Parametrización externo
    consultant_id: models.CharField[str, str] = models.CharField(max_length=64)
    content: models.TextField[str, str] = models.TextField()
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "monitoring_note"
        ordering = ["-created_at"]

    def save(self, *args, update_fields=None, **kwargs):
        if self.pk is not None:
            raise ValueError("MonitoringNote is immutable; updates are not allowed.")
        super().save(*args, **kwargs)

    # backward compatibility
    @property
    def timestamp(self):
        return self.created_at


# Backwards compatibility alias
NotaSeguimiento = MonitoringNote
