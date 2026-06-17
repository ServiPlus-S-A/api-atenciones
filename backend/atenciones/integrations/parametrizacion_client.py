from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient

logger = logging.getLogger("atenciones.integrations.parametrizacion")


@dataclass(frozen=True)
class ConsultorInfoDTO:
    """DTO de respuesta del módulo de Parametrización.

    id: UUID string del consultor.
    disponible: booleano indicando si está disponible.
    aptitudes: tupla de strings representando las aptitudes/roles.
    nombre: nombre completo del consultor.
    role: rol del consultor (ej. 'CONSULTOR').
    """

    id: str
    disponible: bool
    aptitudes: tuple[str, ...] = ()
    nombre: str = ""
    role: str = "CONSULTOR"


# Backwards compatibility alias
ConsultorInfo = ConsultorInfoDTO


class ParametrizacionClient(BaseIntegrationClient):
    """Cliente para interactuar con el módulo de Parametrización."""

    def __init__(self):
        super().__init__(
            getattr(settings, "PARAMETRIZACION_URL", "http://localhost:8002/api")
        )

    def obtener_consultor(self, consultor_id: str) -> ConsultorInfoDTO | None:
        """Obtiene la información de un consultor por ID.

        Retorna None si el consultor no existe.
        Lanza RequestException si hay errores de conexión o el Circuit Breaker está abierto.
        """
        mock_responses = getattr(settings, "PARAMETRIZACION_MOCK_RESPONSES", None)
        if mock_responses is not None:
            respuesta = mock_responses.get(str(consultor_id))
            logger.debug(
                "ParametrizacionClient stub: id=%s respuesta=%s",
                consultor_id,
                respuesta,
            )
            return respuesta

        try:
            data = self._get(f"/consultores/{consultor_id}/")
            return ConsultorInfoDTO(
                id=str(data.get("id", consultor_id)),
                disponible=data.get("disponible", False),
                aptitudes=tuple(data.get("aptitudes", [])),
                nombre=data.get("nombre", f"Consultor {consultor_id}"),
                role=data.get("role", "CONSULTOR"),
            )
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            logger.warning(
                "ParametrizacionClient: error HTTP al consultar consultor %s — %s",
                consultor_id,
                exc,
            )
            raise
        except requests.RequestException as exc:
            logger.warning(
                "ParametrizacionClient: error de red al consultar consultor %s — %s",
                consultor_id,
                exc,
            )
            raise

    def get(self, consultor_id: int | str) -> ConsultorInfoDTO:
        """Deprecated: usar obtener_consultor(). Mantenido por compatibilidad."""
        try:
            result = self.obtener_consultor(str(consultor_id))
            if result is None:
                return ConsultorInfoDTO(
                    id=str(consultor_id),
                    disponible=False,
                    aptitudes=(),
                    nombre=f"Consultor {consultor_id}",
                )
            return result
        except requests.RequestException:
            return ConsultorInfoDTO(
                id=str(consultor_id),
                disponible=False,
                aptitudes=(),
                nombre=f"Consultor {consultor_id}",
            )


parametrizacion_client = ParametrizacionClient()
