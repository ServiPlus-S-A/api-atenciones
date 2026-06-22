from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient

logger = logging.getLogger("atenciones.integrations.solicitudes")


@dataclass(frozen=True)
class SolicitudInfoDTO:
    """DTO de respuesta del módulo de Solicitudes."""

    id: str
    estado: str
    servicio_id: str | None = None
    aptitud_requerida: str | None = None
    cliente_id: str | None = None
    consultor_ids: list[int] | list[str] = field(default_factory=list)


# Backwards compatibility alias
SolicitudInfo = SolicitudInfoDTO


class SolicitudesClient(BaseIntegrationClient):
    """Cliente del módulo de Solicitudes con Circuit Breaker."""

    def __init__(self):
        super().__init__(
            getattr(settings, "SOLICITUDES_URL", "http://localhost:8001/api")
        )
        self.timeout = getattr(settings, "SOLICITUDES_SERVICE_TIMEOUT", self.timeout)

    def obtener_solicitud(self, solicitud_id: str) -> SolicitudInfoDTO | None:
        """Obtiene información de una solicitud por ID."""
        mock_responses = getattr(settings, "SOLICITUDES_MOCK_RESPONSES", None)
        if mock_responses is not None:
            respuesta = mock_responses.get(str(solicitud_id))
            logger.debug(
                "SolicitudesClient stub: id=%s respuesta=%s", solicitud_id, respuesta
            )
            return respuesta

        try:
            data = self._get(f"/solicitudes/{solicitud_id}/")
            return SolicitudInfoDTO(
                id=str(data.get("id", solicitud_id)),
                estado=data.get("estado", "DESCONOCIDO"),
                servicio_id=str(data["servicio_id"])
                if data.get("servicio_id")
                else None,
                aptitud_requerida=data.get("aptitud_requerida"),
                cliente_id=str(data["cliente_id"]) if data.get("cliente_id") else None,
                consultor_ids=data.get("consultor_ids", []),
            )
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            logger.warning(
                "SolicitudesClient: error HTTP al consultar solicitud %s - %s",
                solicitud_id,
                exc,
            )
            raise
        except requests.RequestException as exc:
            logger.warning(
                "SolicitudesClient: error de red al consultar solicitud %s - %s",
                solicitud_id,
                exc,
            )
            raise

    def get_solicitud(self, solicitud_id: str) -> dict | None:
        """
        Retorna dict con {id, estado, client_id, nombre} o None si el circuito está OPEN.
        """
        if time.time() < self.circuit.open_until:
            return None

        if not getattr(settings, "SOLICITUDES_MOCK_ENABLED", True):
            try:
                data = self._get(f"/solicitudes/{solicitud_id}/")
                return {
                    "id": str(data["id"]),
                    "estado": data["estado"],
                    "client_id": data["client_id"],
                    "nombre": data["nombre"],
                }
            except requests.RequestException:
                return None

        # TODO: IMPLEMENTAR cuando el servicio de Solicitudes esté disponible
        # Llamada real (comentada):
        # response = requests.get(
        #     f"{settings.SOLICITUDES_SERVICE_URL}/solicitudes/{solicitud_id}/",
        #     timeout=2,
        # )
        # response.raise_for_status()
        # return response.json()

        return {
            "id": str(solicitud_id),
            "estado": "PENDIENTE",
            "client_id": "mock-client-uuid-001",
            "nombre": f"Solicitud #{solicitud_id}",
        }

    def get(self, solicitud_id: int | str) -> SolicitudInfoDTO:
        """Deprecated: usar obtener_solicitud(). Mantenido por compatibilidad."""
        try:
            result = self.obtener_solicitud(str(solicitud_id))
            if result is None:
                return SolicitudInfoDTO(id=str(solicitud_id), estado="DESCONOCIDO")
            return result
        except requests.RequestException:
            return SolicitudInfoDTO(id=str(solicitud_id), estado="DESCONOCIDO")


solicitudes_client = SolicitudesClient()
