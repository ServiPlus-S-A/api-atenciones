from rest_framework import serializers


class ProgramarAtencionInputSerializer(serializers.Serializer):
    fecha_programada = serializers.DateTimeField(
        required=True,
        help_text="Fecha y hora de inicio de la atención en formato ISO 8601 (Ej: '2026-06-20T10:00:00Z'). Debe alinearse a bloques de 30 minutos.",
    )
    fecha_fin = serializers.DateTimeField(
        required=True,
        help_text="Fecha y hora estimada de finalización de la atención en formato ISO 8601 (Ej: '2026-06-20T11:00:00Z'). Debe ser posterior a la fecha de inicio y alinearse a bloques de 30 minutos.",
    )

    def validate(self, attrs):
        inicio = attrs["fecha_programada"]
        fin = attrs["fecha_fin"]
        if fin <= inicio:
            raise serializers.ValidationError(
                "fecha_fin debe ser posterior a fecha_programada."
            )
        for dt in (inicio, fin):
            if dt.minute % 30 != 0 or dt.second != 0:
                raise serializers.ValidationError(
                    "Las fechas deben alinearse a bloques de 30 minutos.",
                )
        return attrs
