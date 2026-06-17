from dataclasses import dataclass


@dataclass(frozen=True)
class CrearAtencionInputDTO:
    """DTO de entrada para HU-02: Registrar Atención.

    solicitud_id: UUID string de la solicitud externa.
    consultor_ids: tuple inmutable de UUID strings, mínimo 1.
    mensaje_preliminar: texto entre 15 y 1000 chars.
    creado_por_id: opcional mientras auth/RBAC no esté activo.
    """

    solicitud_id: str
    consultor_ids: tuple[str, ...]
    mensaje_preliminar: str
    creado_por_id: str | None = None
