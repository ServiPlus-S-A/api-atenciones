from django import forms

from atenciones.constants import EstadoAtencion
from atenciones.exceptions.custom_exceptions import ParametrosFiltroInvalidos


class AtencionFilterForm(forms.Form):
    """CONCERN-08: solo validador/parser de query params."""

    estado = forms.ChoiceField(
        choices=[(e.value, e.value) for e in EstadoAtencion],
        required=False,
    )

    fecha_inicio = forms.DateField(required=False)

    fecha_fin = forms.DateField(required=False)

    solicitud_id = forms.IntegerField(required=False)

    request_id = forms.CharField(required=False)

    nombre_cliente = forms.CharField(required=False)

    nombre_consultor = forms.CharField(required=False)

    fecha_registro = forms.DateField(required=False)

    @classmethod
    def parse_query_params(cls, query_params) -> dict:
        form = cls(query_params)

        if not form.is_valid():
            raise ParametrosFiltroInvalidos(
                field_errors={k: list(v) for k, v in form.errors.items()}
            )

        return form.cleaned_data
