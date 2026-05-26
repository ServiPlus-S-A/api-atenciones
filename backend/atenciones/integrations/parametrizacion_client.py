from dataclasses import dataclass

import requests
from django.conf import settings

from atenciones.integrations.base_client import BaseIntegrationClient


@dataclass
class ConsultorInfo:
    id: int
    disponible: bool
    aptitudes: list[str]
    nombre: str = ""


class ParametrizacionClient(BaseIntegrationClient):
    def __init__(self):
        super().__init__(settings.PARAMETRIZACION_URL)

    def get(self, consultor_id: int) -> ConsultorInfo:
        try:
            data = self._get(f"/consultores/{consultor_id}/")
            return ConsultorInfo(
                id=consultor_id,
                disponible=data.get("disponible", False),
                aptitudes=data.get("aptitudes", []),
                nombre=data.get("nombre", f"Consultor {consultor_id}"),
            )
        except requests.RequestException:
            return ConsultorInfo(id=consultor_id, disponible=False, aptitudes=[])


parametrizacion_client = ParametrizacionClient()
