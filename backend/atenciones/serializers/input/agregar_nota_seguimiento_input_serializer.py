from rest_framework import serializers

from atenciones.constants import ERR_NOTA_SEGUIMIENTO


class AgregarNotaSeguimientoInputSerializer(serializers.Serializer):
    """
    HU Consultor - Agregar nota de seguimiento.
    El campo contenido es opcional (el frontend no obliga a escribir),
    pero si se envía debe tener entre 10 y 1000 caracteres.
    """

    contenido = serializers.CharField(
        required=False,
        allow_blank=True,
        min_length=10,
        max_length=1000,
        error_messages={
            "min_length": ERR_NOTA_SEGUIMIENTO,
            "max_length": ERR_NOTA_SEGUIMIENTO,
        },
    )

    def validate_contenido(self, value: str) -> str:
        """
        Solo validar longitud si el consultor escribió algo.
        Si viene vacío/no viene, se retorna vacío (el servicio decidirá no guardar).
        """
        stripped = value.strip() if value else ""
        if stripped and len(stripped) < 10:
            raise serializers.ValidationError(ERR_NOTA_SEGUIMIENTO)
        if stripped and len(stripped) > 1000:
            raise serializers.ValidationError(ERR_NOTA_SEGUIMIENTO)
        return stripped