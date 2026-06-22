from django.core.cache import cache
from django.db import transaction
import requests

from atenciones.audit.audit_service import AuditService
from atenciones.constants import (
    ACTOR_TECNICO_DEFAULT,
    EstadoAtencion,
    Rol,
    TTL_LISTED_CACHE,
)
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.dtos.output.atencion_dto import AtencionDTO
from atenciones.exceptions.custom_exceptions import (
    ConsultorNoDisponible,
    ConsultorNoEncontrado,
    ServicioExternoNoDisponible,
    SolicitudNoAutorizada,
)
from atenciones.integrations.parametrizacion_client import parametrizacion_client
from atenciones.integrations.solicitudes_client import solicitudes_client
from atenciones.repositories.atencion_repository import AtencionRepository
from atenciones.services.atencion_cache_service import AtencionCacheService
from atenciones.tasks.notificacion_tasks import (
    enviar_email_anulacion,
    enviar_email_cliente,
    enviar_notificacion_programacion,
)
from atenciones.validators.atencion_validators import (
    validar_no_anterior_fecha_actual,
    validar_bloques_30min,
    validar_cruce_horario,
    validar_estado_finalizacion,
    validar_longitud_notas,
    validar_transicion_a_finalizada,
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
    def crear(cls, data: dict, user=None) -> AtencionDTO:
        is_auth = user and hasattr(user, "is_authenticated") and user.is_authenticated
        raw_actor_id = data.get("creado_por_id")
        actor_id = (
            str(user.id) if is_auth else str(raw_actor_id or ACTOR_TECNICO_DEFAULT)
        )
        actor_role = getattr(user, "rol", Rol.CONSULTOR) if is_auth else Rol.CONSULTOR
        jwt_subject = (
            cls._jwt_subject(user)
            if is_auth
            else str(raw_actor_id or ACTOR_TECNICO_DEFAULT)
        )

        input_dto = CrearAtencionInputDTO(
            solicitud_id=str(data["solicitud_id"]),
            consultor_ids=tuple(str(cid) for cid in data["consultor_ids"]),
            mensaje_preliminar=data["mensaje_preliminar"],
            creado_por_id=actor_id
            if is_auth
            else (str(raw_actor_id) if raw_actor_id else None),
        )

        # 1. Validar solicitud fuera de transacción
        try:
            solicitud = solicitudes_client.obtener_solicitud(input_dto.solicitud_id)
        except requests.RequestException:
            raise ServicioExternoNoDisponible()

        if solicitud is None:
            raise SolicitudNoAutorizada(
                "La solicitud ingresada no existe en el sistema o no está autorizada para atención."
            )
        if solicitud.estado.upper() == "DESCONOCIDO":
            raise ServicioExternoNoDisponible()
        if solicitud.estado.upper() != "PENDIENTE":
            raise SolicitudNoAutorizada(
                "La solicitud ingresada no existe en el sistema o no está autorizada para atención."
            )

        # 2. Validar consultores fuera de transacción
        consultores_info = []
        for cid in input_dto.consultor_ids:
            try:
                info = parametrizacion_client.obtener_consultor(cid)
            except requests.RequestException:
                raise ServicioExternoNoDisponible()

            if info is None:
                raise ConsultorNoEncontrado(
                    f"Consultor {cid} no encontrado en el sistema."
                )
            if not info.disponible:
                raise ConsultorNoDisponible(f"Consultor {cid} no está disponible.")
            if (
                solicitud.aptitud_requerida
                and solicitud.aptitud_requerida not in info.aptitudes
            ):
                raise ConsultorNoDisponible(
                    f"Consultor {cid} no tiene la aptitud requerida para este servicio."
                )
            consultores_info.append(info)

        # 3. Persistencia atómica
        with transaction.atomic():
            dto = AtencionRepository.guardar(input_dto, consultores_info)

            # Registrar auditoría dentro de la transacción
            AuditService.registrar(
                "CREAR",
                actor_id,
                actor_role,
                dto.id,
                {
                    "solicitud_id": str(input_dto.solicitud_id),
                    "consultor_ids": list(input_dto.consultor_ids),
                    "mensaje_preliminar_length": len(input_dto.mensaje_preliminar),
                },
                jwt_subject,
            )

            # Invalidación de caché y encolar tarea asíncrona on_commit
            transaction.on_commit(
                lambda: AtencionCacheService.invalidate_after_create(
                    created_by=input_dto.creado_por_id,
                    consultor_ids=list(input_dto.consultor_ids),
                )
            )
            transaction.on_commit(
                lambda: enviar_notificacion_programacion.delay(dto.id)
            )

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
        validar_no_anterior_fecha_actual(input_dto.fecha_programada)
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
        validar_cruce_horario(
            consultor_ids, input_dto.fecha_programada, input_dto.fecha_fin, cruces
        )
        dto = AtencionRepository.programar(input_dto)
        _invalidate_cache(user)
        cache.delete(f"atencion_detalle:{dto.id}")
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
            estado=data["estado"],
            notas_finales=data["notas_finales"],
            consultor_id=user.id,
        )
        validar_estado_finalizacion(input_dto.estado)
        validar_longitud_notas(input_dto.notas_finales)
        atencion = AtencionRepository.obtener_por_id(atencion_id)
        validar_transicion_a_finalizada(atencion.estado)
        dto = AtencionRepository.finalizar(input_dto)
        _invalidate_cache(user)
        cache.delete(f"atencion_detalle:{dto.id}")
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
        cache.delete(f"atencion_detalle:{dto.id}")
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
