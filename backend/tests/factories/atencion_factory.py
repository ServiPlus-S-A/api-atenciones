import factory
from factory.django import DjangoModelFactory

from atenciones.constants import EstadoAtencion
from atenciones.models import Atencion


class AtencionFactory(DjangoModelFactory):
    class Meta:
        model = Atencion

    estado = EstadoAtencion.AGENDADA
    solicitud_id = factory.Sequence(lambda n: n + 1)
    creado_por_id = 1


class AtencionFinalizadaFactory(AtencionFactory):
    estado = EstadoAtencion.FINALIZADA
    notas_finales = "Notas finales de prueba con más de veinte caracteres."


class AtencionAnuladaFactory(AtencionFactory):
    estado = EstadoAtencion.ANULADA
    motivo_anulacion = "Motivo de anulación de prueba válido."
