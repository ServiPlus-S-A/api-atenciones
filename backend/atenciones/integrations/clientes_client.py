from __future__ import annotations

import logging
import time

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient

logger = logging.getLogger("atenciones.integrations.clientes")


class ClientesClient(BaseIntegrationClient):
    """Cliente para el módulo de Clientes con Circuit Breaker."""

    def __init__(self):
        super().__init__(
            getattr(settings, "CLIENTES_SERVICE_URL", "http://localhost:8002")
        )
        self.timeout = getattr(settings, "CLIENTES_SERVICE_TIMEOUT", self.timeout)

    def get_contacto_cliente(self, client_id: str) -> dict | None:
        """
        Retorna dict con {nombre_completo, telefono, correo_electronico}
        o None si el circuito está OPEN.
        Para esta tarea solo se usa el campo nombre_completo.
        """
        if time.time() < self.circuit.open_until:
            return None

        if not getattr(settings, "CLIENTES_MOCK_ENABLED", True):
            try:
                data = self._get(f"/clientes/{client_id}/contacto/")
                return {
                    "nombre_completo": data["nombre_completo"],
                    "telefono": data.get("telefono"),
                    "correo_electronico": data.get("correo_electronico"),
                }
            except requests.RequestException:
                return None

        # TODO: IMPLEMENTAR cuando el servicio de Clientes esté disponible
        # Llamada real (comentada):
        # response = requests.get(
        #     f"{settings.CLIENTES_SERVICE_URL}/clientes/{client_id}/contacto/",
        #     timeout=2,
        # )
        # response.raise_for_status()
        # return response.json()

        return {
            "nombre_completo": "Cliente Mock Temporal",
            "telefono": "3000000000",
            "correo_electronico": "mock.cliente@example.com",
        }


clientes_client = ClientesClient()
