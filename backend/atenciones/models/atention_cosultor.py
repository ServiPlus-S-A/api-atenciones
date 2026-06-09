from __future__ import annotations

from django.db import models

from .atention import Atention


class AtentionConsultant(models.Model):
    atention: models.ForeignKey[Atention, Atention] = models.ForeignKey(
        Atention,
        on_delete=models.CASCADE,
        related_name="consultants_rel",
        db_column="atention_fk",
    )
    consultant_id: models.IntegerField[int, int] = models.IntegerField()
    is_leader: models.BooleanField[bool, bool] = models.BooleanField(default=False)

    class Meta:
        db_table = "atention_consultant"
        unique_together = ("atention", "consultant_id")


# Backwards compatibility alias
AtencionConsultor = AtentionConsultant
