from dataclasses import dataclass


@dataclass(frozen=True)
class AnularAtencionInputDTO:
    atencion_id: int
    motivo_anulacion: str
    coordinador_id: int
