from rest_framework import serializers


class CrearAtencionInputSerializer(serializers.Serializer):
    solicitud_id = serializers.UUIDField(required=True)
    consultor_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        required=True,
    )
    mensaje_preliminar = serializers.CharField(
        min_length=15,
        max_length=1000,
        required=True,
        error_messages={
            "min_length": "El diagnostico debe tener entre 15 y 1000 caracteres.",
            "max_length": "El diagnostico debe tener entre 15 y 1000 caracteres.",
        },
    )
    creado_por_id = serializers.CharField(required=False, allow_null=True)

    def validate_consultor_ids(self, value):
        str_ids = [str(v) for v in value]
        if len(str_ids) != len(set(str_ids)):
            raise serializers.ValidationError(
                "consultor_ids no puede tener duplicados."
            )
        return str_ids
