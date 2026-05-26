from dataclasses import dataclass

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient


@dataclass
class SolicitudInfo:
    id: int
    estado: str
    consultor_ids: list[int]


class SolicitudesClient(BaseIntegrationClient):
    def __init__(self):
        super().__init__(settings.SOLICITUDES_URL)

    def get(self, solicitud_id: int) -> SolicitudInfo:
        try:
            data = self._get(f"/solicitudes/{solicitud_id}/")
            return SolicitudInfo(
                id=data["id"],
                estado=data.get("estado", "DESCONOCIDO"),
                consultor_ids=data.get("consultor_ids", []),
            )
        except requests.RequestException:
            return SolicitudInfo(id=solicitud_id, estado="DESCONOCIDO", consultor_ids=[])


solicitudes_client = SolicitudesClient()
