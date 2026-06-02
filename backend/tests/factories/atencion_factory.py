import factory
from factory.django import DjangoModelFactory

from atenciones.constants import EstadoAtencion
from atenciones.models import Atencion


class AtencionFactory(DjangoModelFactory):
    class Meta:
        model = Atencion

    status = EstadoAtencion.AGENDADA
    request_id = factory.Sequence(lambda n: n + 1)
    created_by = 1


class AtencionFinalizadaFactory(AtencionFactory):
    status = EstadoAtencion.FINALIZADA
    final_note = "Notas finales de prueba con más de veinte caracteres."


class AtencionAnuladaFactory(AtencionFactory):
    status = EstadoAtencion.ANULADA
    cancellation_reason = "Motivo de anulación de prueba válido."
