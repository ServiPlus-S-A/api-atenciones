from django.core.cache import cache
from django.db import transaction

from atenciones.audit.audit_service import AuditService
from atenciones.constants import EstadoAtencion, Rol, TTL_LISTED_CACHE
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.dtos.output.atencion_dto import AtencionDTO
from atenciones.exceptions.custom_exceptions import (
    ConsultorNoDisponible,
    ServicioExternoNoDisponible,
    SolicitudNoAutorizada,
)
from atenciones.integrations.parametrizacion_client import parametrizacion_client
from atenciones.integrations.solicitudes_client import solicitudes_client
from atenciones.repositories.atencion_repository import AtencionRepository
from atenciones.tasks.notificacion_tasks import (
    enviar_email_anulacion,
    enviar_email_cliente,
    enviar_notificacion_programacion,
)
from atenciones.validators.atencion_validators import (
    validar_anticipacion_24h,
    validar_bloques_30min,
    validar_cruce_horario,
    validar_longitud_notas,
    validar_transicion_estado,
)


def _cache_key(user_id: int, rol: str) -> str:
    return f"listado_{rol}_{user_id}"


def _invalidate_cache(user) -> None:
    cache.delete(_cache_key(user.id, getattr(user, "rol", "")))


class AtencionService:
    """CONCERN-01/08: convierte dict → InputDTO; cache-aside en listados."""

    @staticmethod
    def _jwt_subject(user) -> str:
        return str(getattr(user, "username", user.id))

    @classmethod
    @transaction.atomic
    def crear(cls, data: dict, user) -> AtencionDTO:
        input_dto = CrearAtencionInputDTO(
            solicitud_id=data["solicitud_id"],
            consultor_ids=data["consultor_ids"],
            mensaje_preliminar=data["mensaje_preliminar"],
            creado_por_id=user.id,
        )
        solicitud = solicitudes_client.get(input_dto.solicitud_id)
        if solicitud.estado == "DESCONOCIDO":
            raise ServicioExternoNoDisponible()
        if solicitud.estado != "Pendiente":
            raise SolicitudNoAutorizada("La solicitud no está en estado Pendiente.")
        for cid in input_dto.consultor_ids:
            info = parametrizacion_client.get(cid)
            if not info.disponible:
                raise ConsultorNoDisponible()
        dto = AtencionRepository.guardar(input_dto)
        _invalidate_cache(user)
        AuditService.registrar(
            "CREAR",
            user.id,
            getattr(user, "rol", Rol.COORDINADOR),
            dto.id,
            {"solicitud_id": dto.solicitud_id},
            cls._jwt_subject(user),
        )
        enviar_notificacion_programacion.delay(dto.id)
        return dto

    @classmethod
    @transaction.atomic
    def programar(cls, atencion_id: int, data: dict, user) -> AtencionDTO:
        input_dto = ProgramarAtencionInputDTO(
            atencion_id=atencion_id,
            fecha_programada=data["fecha_programada"],
            fecha_fin=data["fecha_fin"],
            programado_por_id=user.id,
        )
        validar_anticipacion_24h(input_dto.fecha_programada)
        validar_bloques_30min(input_dto.fecha_programada, input_dto.fecha_fin)
        atencion = AtencionRepository.obtener_por_id(atencion_id)
        validar_transicion_estado(atencion.estado, EstadoAtencion.AGENDADA)
        consultor_ids = [c.id for c in atencion.consultores]
        cruces = AtencionRepository.buscar_cruces(
            consultor_ids,
            input_dto.fecha_programada,
            input_dto.fecha_fin,
            excluir_atencion_id=atencion_id,
        )
        validar_cruce_horario(consultor_ids, input_dto.fecha_programada, input_dto.fecha_fin, cruces)
        dto = AtencionRepository.programar(input_dto)
        _invalidate_cache(user)
        AuditService.registrar(
            "PROGRAMAR",
            user.id,
            getattr(user, "rol", ""),
            dto.id,
            {"fecha_programada": str(dto.fecha_programada)},
            cls._jwt_subject(user),
        )
        enviar_notificacion_programacion.delay(dto.id)
        return dto

    @classmethod
    @transaction.atomic
    def finalizar(cls, atencion_id: int, data: dict, user) -> AtencionDTO:
        input_dto = FinalizarAtencionInputDTO(
            atencion_id=atencion_id,
            notas_finales=data["notas_finales"],
            consultor_id=user.id,
        )
        validar_longitud_notas(input_dto.notas_finales)
        atencion = AtencionRepository.obtener_por_id(atencion_id)
        validar_transicion_estado(atencion.estado, EstadoAtencion.FINALIZADA)
        dto = AtencionRepository.finalizar(input_dto)
        _invalidate_cache(user)
        AuditService.registrar(
            "FINALIZAR",
            user.id,
            getattr(user, "rol", Rol.CONSULTOR),
            dto.id,
            {"notas_finales_len": len(input_dto.notas_finales)},
            cls._jwt_subject(user),
        )
        enviar_email_cliente.delay(dto.id)
        return dto

    @classmethod
    @transaction.atomic
    def anular(cls, atencion_id: int, data: dict, user) -> AtencionDTO:
        input_dto = AnularAtencionInputDTO(
            atencion_id=atencion_id,
            motivo_anulacion=data["motivo_anulacion"],
            coordinador_id=user.id,
        )
        atencion = AtencionRepository.obtener_por_id(atencion_id)
        validar_transicion_estado(atencion.estado, EstadoAtencion.ANULADA)
        dto = AtencionRepository.anular(input_dto)
        _invalidate_cache(user)
        AuditService.registrar(
            "ANULAR",
            user.id,
            getattr(user, "rol", Rol.COORDINADOR),
            dto.id,
            {"motivo": input_dto.motivo_anulacion},
            cls._jwt_subject(user),
        )
        enviar_email_anulacion.delay(dto.id)
        return dto

    @classmethod
    def listar_para_usuario(cls, user, filtros: dict) -> list[AtencionDTO]:
        rol = getattr(user, "rol", Rol.CLIENTE)
        estados_excluidos = None
        if rol == Rol.CONSULTOR:
            estados_excluidos = [EstadoAtencion.ANULADA.value]
            filtros = {**filtros, "consultor_id": user.id}
        elif rol == Rol.CLIENTE:
            estados_excluidos = [EstadoAtencion.ANULADA.value]

        key = _cache_key(user.id, rol)
        cached = cache.get(key)
        if cached is not None and not filtros:
            return cached

        result = AtencionRepository.listar(filtros, estados_excluidos)
        if not filtros:
            cache.set(key, result, TTL_LISTED_CACHE)
        return result

    @classmethod
    def detalle(cls, atencion_id: int) -> AtencionDTO:
        return AtencionRepository.obtener_por_id(atencion_id)
