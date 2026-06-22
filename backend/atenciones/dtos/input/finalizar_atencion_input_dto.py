from dataclasses import dataclass


@dataclass(frozen=True)
class FinalizarAtencionInputDTO:
    atencion_id: int
    estado: str
    notas_finales: str
    consultor_id: int
