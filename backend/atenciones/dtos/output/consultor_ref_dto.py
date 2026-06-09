from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultantRefDTO:
    id: int
    name: str
    is_leader: bool

    # Alias en español para integrarse con serializers existentes.
    @property
    def nombre(self) -> str:
        return self.name

    @property
    def es_lider(self) -> bool:
        return self.is_leader


# Backwards compatibility alias
ConsultorRefDTO = ConsultantRefDTO
