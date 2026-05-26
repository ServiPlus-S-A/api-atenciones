from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultorRefDTO:
    id: int
    nombre: str
    es_lider: bool
