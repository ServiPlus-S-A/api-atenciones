from rest_framework import serializers


class VerificarCruceInputSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateTimeField(required=True)
    fecha_fin = serializers.DateTimeField(required=True)
    consultor_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    atencion_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        inicio = attrs["fecha_inicio"]
        fin = attrs["fecha_fin"]
        if fin <= inicio:
            raise serializers.ValidationError(
                "fecha_fin debe ser posterior a fecha_inicio."
            )
        for dt in (inicio, fin):
            if dt.minute % 30 != 0 or dt.second != 0:
                raise serializers.ValidationError(
                    "Las fechas deben alinearse a bloques de 30 minutos.",
                )
        return attrs
