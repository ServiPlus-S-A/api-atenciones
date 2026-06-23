from rest_framework import serializers


MAX_PAGE_SIZE = 50


class ListarAtencionInputSerializer(serializers.Serializer):
    """CONCERN-07: paginación del listado (filtros en AtencionFilterForm)."""

    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=10, min_value=1)

    def validate_page_size(self, value: int) -> int:
        return min(value, MAX_PAGE_SIZE)
