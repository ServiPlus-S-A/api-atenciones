import django_filters

from atenciones.constants import EstadoAtencion


class AtencionFilterSet(django_filters.FilterSet):
    """CONCERN-08: solo validador/parser de query params; no toca QuerySet."""

    estado = django_filters.ChoiceFilter(choices=[(e.value, e.value) for e in EstadoAtencion])
    fecha_inicio = django_filters.DateFilter()
    fecha_fin = django_filters.DateFilter()
    solicitud_id = django_filters.NumberFilter()

    @classmethod
    def parse_query_params(cls, query_params) -> dict:
        fs = cls(data=query_params)
        fs.is_valid()
        return fs.form.cleaned_data
