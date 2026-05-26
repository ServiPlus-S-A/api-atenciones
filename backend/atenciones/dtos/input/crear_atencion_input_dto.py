from dataclasses import dataclass


@dataclass(frozen=True)
class CrearAtencionInputDTO:
    solicitud_id: int
    consultor_ids: list[int]
    mensaje_preliminar: str
    creado_por_id: int
