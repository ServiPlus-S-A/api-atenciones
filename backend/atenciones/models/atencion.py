from django.db import models

from atenciones.constants import EstadoAtencion


class Atencion(models.Model):
    estado = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EstadoAtencion],
        default=EstadoAtencion.AGENDADA,
    )
    solicitud_id = models.IntegerField(db_index=True)
    fecha_programada = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    notas_finales = models.TextField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    creado_por_id = models.IntegerField()
    motivo_anulacion = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "atencion"
        indexes = [
            models.Index(fields=["estado", "fecha_programada"]),
        ]

    def __str__(self):
        return f"Atencion({self.pk}, {self.estado})"
