from __future__ import annotations

from datetime import datetime

from django.db import models

from atenciones.models.atencion import Atencion


class NotaSeguimiento(models.Model):
    atencion: models.ForeignKey[Atencion, Atencion] = models.ForeignKey(
        Atencion,
        on_delete=models.CASCADE,
        related_name="notas",
        db_column="atencion_fk",
    )
    consultor_id: models.IntegerField[int, int] = models.IntegerField()
    contenido: models.TextField[str, str] = models.TextField()
    timestamp: models.DateTimeField[datetime, datetime] = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "nota_seguimiento"
        ordering = ["-timestamp"]

    def save(self, *args, update_fields=None, **kwargs):
        if self.pk is not None:
            raise ValueError("NotaSeguimiento es inmutable; no se permite actualización.")
        super().save(*args, **kwargs)
