from rest_framework import serializers


class CrearAtencionInputSerializer(serializers.Serializer):
    solicitud_id = serializers.IntegerField(required=True)
    consultor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        required=True,
    )
    mensaje_preliminar = serializers.CharField(
        min_length=15, max_length=1000, required=True
    )
