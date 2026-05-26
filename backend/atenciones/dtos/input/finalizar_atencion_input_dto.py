from dataclasses import dataclass


@dataclass(frozen=True)
class FinalizarAtencionInputDTO:
    atencion_id: int
    notas_finales: str
    consultor_id: int
