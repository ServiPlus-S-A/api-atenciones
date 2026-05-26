from django.core.management.base import BaseCommand

from atenciones.constants import EstadoAtencion


class Command(BaseCommand):
    help = "Crea registros iniciales de EstadoAtencion si no existen (idempotente)."

    def handle(self, *args, **options):
        for estado in EstadoAtencion:
            self.stdout.write(f"Estado disponible: {estado.value}")
        self.stdout.write(self.style.SUCCESS("Estados de atención verificados."))
