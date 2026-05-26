from atenciones.audit.audit_service import AuditService
from atenciones.constants import Rol
from atenciones.dtos.output.nota_seguimiento_dto import NotaSeguimientoDTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada, SolicitudNoAutorizada
from atenciones.repositories.atencion_repository import AtencionRepository
from atenciones.repositories.nota_seguimiento_repository import (
    AgregarNotaInputDTO,
    NotaSeguimientoRepository,
)


class NotaSeguimientoService:
    @classmethod
    def agregar_nota(cls, user, atencion_id: int, contenido: str) -> NotaSeguimientoDTO:
        try:
            AtencionRepository.obtener_por_id(atencion_id)
        except AtencionNoEncontrada:
            raise
        rol = getattr(user, "rol", "")
        if rol not in (Rol.CONSULTOR, Rol.COORDINADOR):
            raise SolicitudNoAutorizada()
        dto = NotaSeguimientoRepository.guardar_nota(
            AgregarNotaInputDTO(
                atencion_id=atencion_id,
                consultor_id=user.id,
                contenido=contenido,
            ),
        )
        AuditService.registrar(
            "AGREGAR_NOTA",
            user.id,
            rol,
            atencion_id,
            {"nota_id": dto.id},
            str(getattr(user, "username", user.id)),
        )
        return dto

    @classmethod
    def listar(cls, user, atencion_id: int) -> list[NotaSeguimientoDTO]:
        AtencionRepository.obtener_por_id(atencion_id)
        consultor_id = user.id if getattr(user, "rol", "") == Rol.CONSULTOR else None
        return NotaSeguimientoRepository.listar_por_atencion(atencion_id, consultor_id)
