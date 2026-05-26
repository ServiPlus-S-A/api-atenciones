from rest_framework import serializers

from atenciones.constants import EstadoAtencion


class ListarAtencionInputSerializer(serializers.Serializer):
    """CONCERN-07: valida query params HU-12 + HU-14."""

    estado = serializers.ChoiceField(
        choices=[e.value for e in EstadoAtencion],
        required=False,
    )
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    solicitud_id = serializers.IntegerField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=10, min_value=1, max_value=50)
