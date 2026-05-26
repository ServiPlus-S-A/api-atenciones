from rest_framework import serializers


class FinalizarAtencionInputSerializer(serializers.Serializer):
    notas_finales = serializers.CharField(min_length=20, max_length=2000, required=True)
