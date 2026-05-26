from django.db import models

from atenciones.models.atencion import Atencion


class AtencionConsultor(models.Model):
    atencion = models.ForeignKey(
        Atencion,
        on_delete=models.CASCADE,
        related_name="consultores_rel",
        db_column="atencion_fk",
    )
    consultor_id = models.IntegerField()
    es_lider = models.BooleanField(default=False)

    class Meta:
        db_table = "atencion_consultor"
        unique_together = ("atencion", "consultor_id")
