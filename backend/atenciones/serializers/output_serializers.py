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


class AtencionDetalleConsultorOutputSerializer(serializers.Serializer):
    """Serializer para el detalle de atención visto por un consultor (HU-05)"""

    id = serializers.IntegerField(read_only=True)
    request_id = serializers.CharField(read_only=True)
    solicitud_nombre = serializers.CharField(read_only=True, allow_null=True)
    scheduled_date = serializers.DateTimeField(read_only=True, allow_null=True)
    closing_date = serializers.DateTimeField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True)
    diagnostico_inicial = serializers.CharField(read_only=True, allow_null=True)
    notas = MonitoringNoteOutputSerializer(many=True, read_only=True)
    mensaje_bitacora = serializers.CharField(read_only=True, allow_null=True)
    acciones_disponibles = serializers.DictField(
        child=serializers.BooleanField(), read_only=True
    )

    # Campos de contacto (HU-01)
    contacto_nombre = serializers.CharField(read_only=True)
    contacto_telefono = serializers.CharField(read_only=True)
    contacto_correo = serializers.CharField(read_only=True)
    contacto_disponible = serializers.BooleanField(read_only=True)
    contacto_error_msg = serializers.CharField(read_only=True, allow_null=True)


class ConsultorDetalleClienteOutputSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    is_leader = serializers.BooleanField()
    role = serializers.CharField()


class AtencionDetalleClienteOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    request_id = serializers.CharField()
    solicitud_nombre = serializers.CharField(allow_null=True)
    consultores = ConsultorDetalleClienteOutputSerializer(many=True)
    scheduled_date = serializers.DateTimeField(
        allow_null=True,
        format="%d/%m/%Y %H:%M",
    )
    status = serializers.CharField()
    diagnostico_inicial = serializers.CharField(allow_null=True)
    notas = MonitoringNoteOutputSerializer(many=True)
    mensaje_bitacora = serializers.CharField(allow_null=True)
