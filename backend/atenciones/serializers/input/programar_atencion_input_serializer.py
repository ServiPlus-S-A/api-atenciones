from rest_framework import serializers


class ProgramarAtencionInputSerializer(serializers.Serializer):
    fecha_programada = serializers.DateTimeField(required=True)
    fecha_fin = serializers.DateTimeField(required=True)

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
