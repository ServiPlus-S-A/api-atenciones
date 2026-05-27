from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.db import models

from atenciones.constants import EstadoAtencion


class Atencion(models.Model):
    estado: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EstadoAtencion],
        default=EstadoAtencion.AGENDADA,
    )
    solicitud_id: models.IntegerField[int, int] = models.IntegerField(db_index=True)
    fecha_programada: models.DateTimeField[datetime | None, datetime | None] = models.DateTimeField(null=True, blank=True)
    fecha_fin: models.DateTimeField[datetime | None, datetime | None] = models.DateTimeField(null=True, blank=True)
    notas_finales: models.TextField[str | None, str | None] = models.TextField(null=True, blank=True)
    fecha_cierre: models.DateTimeField[datetime | None, datetime | None] = models.DateTimeField(null=True, blank=True)
    creado_por_id: models.IntegerField[int, int] = models.IntegerField()
    motivo_anulacion: models.TextField[str | None, str | None] = models.TextField(null=True, blank=True)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from atenciones.models.atencion_consultor import AtencionConsultor

        consultores_rel: models.Manager[AtencionConsultor]

    class Meta:
        db_table = "atencion"
        indexes = [
            models.Index(fields=["estado", "fecha_programada"]),
        ]

    def __str__(self):
        return f"Atencion({self.pk}, {self.estado})"
