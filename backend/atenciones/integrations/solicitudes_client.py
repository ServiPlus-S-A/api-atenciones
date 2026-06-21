"""
Integration Layer — SolicitudesClient

Contrato estable y mockeable para el módulo de Solicitudes.
El servicio de Solicitudes aún no está levantado (HU-02).
Para activar el cliente real, configurar SOLICITUDES_URL en settings.
Para usar el stub en desarrollo/test, configurar SOLICITUDES_MOCK_ENABLED=True
y SOLICITUDES_MOCK_RESPONSES en settings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient

logger = logging.getLogger("atenciones.integrations.solicitudes")


@dataclass(frozen=True)
class SolicitudInfoDTO:
    """DTO de respuesta del módulo de Solicitudes.

    Contrato estable: no cambiar nombres sin actualizar SolicitudesClient.
    id: UUID string de la solicitud.
    estado: estado de la solicitud (ej. 'PENDIENTE', 'ATENDIDA', etc.)
    servicio_id: ID del servicio solicitado (para validar aptitud de consultores).
    aptitud_requerida: aptitud mínima requerida para atender la solicitud.
    cliente_id: ID del cliente que realizó la solicitud.
    """

    id: str
    estado: str
    servicio_id: str | None = None
    aptitud_requerida: str | None = None
    cliente_id: str | None = None
    consultor_ids: list[int] | list[str] = field(default_factory=list)


# Backwards compatibility alias (código existente usa SolicitudInfo)
SolicitudInfo = SolicitudInfoDTO


class SolicitudesClient(BaseIntegrationClient):
    """Cliente del módulo de Solicitudes.

    Implementa el patrón Circuit Breaker vía BaseIntegrationClient.
    Retorna None cuando la solicitud no existe (en lugar de lanzar excepción),
    para permitir al Service tomar la decisión de negocio.
    """

    def __init__(self):
        super().__init__(
            getattr(settings, "SOLICITUDES_URL", "http://localhost:8001/api")
        )

    def obtener_solicitud(self, solicitud_id: str) -> SolicitudInfoDTO | None:
        """Obtiene información de una solicitud por ID.

        Retorna None si la solicitud no existe.
        Lanza RequestException si hay errores de conexión o el Circuit Breaker está abierto.
        """
        # Modo stub: permite pruebas sin servicio externo real
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
                "SolicitudesClient: error HTTP al consultar solicitud %s — %s",
                solicitud_id,
                exc,
            )
            raise
        except requests.RequestException as exc:
            logger.warning(
                "SolicitudesClient: error de red al consultar solicitud %s — %s",
                solicitud_id,
                exc,
            )
            raise

    # Backwards compatibility: mantiene el método get() original
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
