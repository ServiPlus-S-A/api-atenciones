from __future__ import annotations

from django.db import models
from django.db.models import Q

from .atention import Atention


class AtentionConsultant(models.Model):
    atention: models.ForeignKey[Atention, Atention] = models.ForeignKey(
        Atention,
        on_delete=models.CASCADE,
        related_name="consultants_rel",
        db_column="atention_fk",
    )
    # HU-02: consultant_id es UUID string del módulo de Parametrización externo
    consultant_id: models.CharField[str, str] = models.CharField(max_length=64)
    consultant_name: models.CharField[str | None, str | None] = models.CharField(
        max_length=255, null=True, blank=True, db_index=True
    )
    is_leader: models.BooleanField[bool, bool] = models.BooleanField(default=False)

    class Meta:
        db_table = "atention_consultant"
        unique_together = (("atention", "consultant_id"),)
        constraints = [
            models.UniqueConstraint(
                fields=["atention"],
                condition=Q(is_leader=True),
                name="unique_leader_per_atention",
            )
        ]


# Backwards compatibility alias
AtencionConsultor = AtentionConsultant
