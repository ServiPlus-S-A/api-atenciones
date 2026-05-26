from rest_framework import serializers


class AnularAtencionInputSerializer(serializers.Serializer):
    motivo_anulacion = serializers.CharField(min_length=15, max_length=500, required=True)
