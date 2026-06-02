from rest_framework import serializers


class ListarAtencionInputSerializer(serializers.Serializer):
    """CONCERN-07: paginación del listado (filtros en AtencionFilterForm)."""

    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=10, min_value=1, max_value=50)
