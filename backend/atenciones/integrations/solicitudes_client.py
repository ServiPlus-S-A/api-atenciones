from __future__ import annotations

import logging
from dataclasses import dataclass, field

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient

from typing import Optional, Mapping, Any

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

    def get_solicitud(
        self, solicitud_id: int | str, params: Optional[Mapping[str, Any]] = None
    ) -> dict:
        path = f"/solicitudes/{solicitud_id}"
        return self._get(path, params=params)

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

    def buscar_solicitudes_por_cliente_nombre(self, cliente_nombre: str) -> list[str]:
        """Busca solicitudes asociadas a un nombre de cliente.

        En modo `mock` recorre `SOLICITUDES_MOCK_RESPONSES` y compara
        contra la clave `cliente_nombre` o `cliente_id` si está disponible.
        En modo real intenta invocar un endpoint de búsqueda (si existe).
        Retorna lista de `id` (strings)."""
        mock_responses = getattr(settings, "SOLICITUDES_MOCK_RESPONSES", None)
        if mock_responses is not None:
            result = []
            for sid, data in mock_responses.items():
                # data puede ser un dict o un SolicitudInfoDTO-like
                nombre = None
                if isinstance(data, dict):
                    nombre = data.get("cliente_nombre") or data.get("cliente_id")
                else:
                    nombre = getattr(data, "cliente_id", None)
                if nombre and cliente_nombre.lower() in str(nombre).lower():
                    result.append(str(sid))
            logger.debug(
                "SolicitudesClient.stub: buscar cliente_nombre=%s -> %s",
                cliente_nombre,
                result,
            )
            return result

        try:
            data = self._get("/solicitudes/", params={"cliente_nombre": cliente_nombre})
            # esperamos una lista de objetos con 'id'
            return [str(item.get("id")) for item in data]
        except requests.RequestException:
            logger.warning(
                "SolicitudesClient: error al buscar solicitudes por cliente %s",
                cliente_nombre,
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
