from rest_framework import serializers

from atenciones.constants import (
    ERR_ESTADO_NO_PERMITIDO,
    ERR_NOTAS_FINALES_LARGAS,
    ERR_NOTAS_FINALES_OBLIGATORIAS,
    EstadoAtencion,
)


class FinalizarAtencionInputSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=[EstadoAtencion.FINALIZADA],
        required=True,
        error_messages={
            "required": ERR_ESTADO_NO_PERMITIDO,
            "invalid_choice": ERR_ESTADO_NO_PERMITIDO,
        },
    )
    notas_finales = serializers.CharField(
        min_length=20,
        max_length=2000,
        required=True,
        allow_blank=False,
        error_messages={
            "required": ERR_NOTAS_FINALES_OBLIGATORIAS,
            "blank": ERR_NOTAS_FINALES_OBLIGATORIAS,
            "min_length": ERR_NOTAS_FINALES_OBLIGATORIAS,
            "max_length": ERR_NOTAS_FINALES_LARGAS,
        },
    )

    def validate_notas_finales(self, value: str) -> str:
        if len(value.strip()) < 20:
            raise serializers.ValidationError(ERR_NOTAS_FINALES_OBLIGATORIAS)
        return value
