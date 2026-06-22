from rest_framework import serializers


class MonitoringNoteOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()
    created_by = serializers.CharField(source="consultant_id")


class AtencionDetalleCoordinadorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    request_id = serializers.CharField()
    solicitud_nombre = serializers.CharField(allow_null=True)
    cliente_nombre = serializers.CharField(allow_null=True)
    scheduled_date = serializers.DateTimeField(allow_null=True)
    closing_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    diagnostico_inicial = serializers.CharField(allow_null=True)
    notas = MonitoringNoteOutputSerializer(many=True)
    mensaje_bitacora = serializers.CharField(allow_null=True)
    acciones_disponibles = serializers.DictField(child=serializers.BooleanField())
