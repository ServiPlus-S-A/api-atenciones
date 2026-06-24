import logging

from django.core.cache import cache
from django.db import Error as DBError

from atenciones.dtos.output.consultor_ref_dto import ConsultantRefDTO
from atenciones.dtos.output.atencion_detalle_coordinador_dto import (
    AtencionDetalleClienteDTO,
    AtencionDetalleCoordinadorDTO,
)

from atenciones.exceptions import (
    AtencionDoesNotExist,
    AtencionPermissionDenied,
    AtencionServiceUnavailableError,
)
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.integrations.parametrizacion_client import parametrizacion_client
from atenciones.integrations.clientes_client import clientes_client
from atenciones.integrations.solicitudes_client import solicitudes_client
from atenciones.repositories.atencion_repository import AtencionRepository
from atenciones.repositories.nota_seguimiento_repository import (
    NotaSeguimientoRepository,
)

logger = logging.getLogger("atenciones.services.atencion_detalle")


class AtencionDetalleService:
    @staticmethod
    def obtener_detalle_coordinador(atention_id: int) -> AtencionDetalleCoordinadorDTO:
        key = f"atencion_detalle:{atention_id}"

        try:
            cached_dto = cache.get(key)
            if cached_dto is not None:
                return cached_dto
        except Exception as exc:
            logger.warning("Cache access error: %s", exc)

        try:
            atencion = AtencionRepository.obtener_por_id(atention_id)
        except AtencionNoEncontrada as exc:
            raise AtencionDoesNotExist() from exc
        except DBError as exc:
            logger.exception("Database error retrieving attention detail")
            raise AtencionServiceUnavailableError() from exc

        try:
            nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atention_id)
            diagnostico_inicial = nota_inicial.content if nota_inicial else None
            notas = NotaSeguimientoRepository.listar_por_atencion(atention_id)
        except DBError as exc:
            logger.exception("Database error retrieving attention notes")
            raise AtencionServiceUnavailableError() from exc

        mensaje_bitacora = AtencionDetalleService._mensaje_bitacora_vacia(notas)

        solicitud_nombre, client_id = AtencionDetalleService._obtener_solicitud_info(
            str(atencion.solicitud_id)
        )
        cliente_nombre = AtencionDetalleService._obtener_cliente_nombre(client_id)

        acciones_disponibles = AtencionDetalleService._calcular_acciones_disponibles(
            atencion.estado
        )

        dto = AtencionDetalleCoordinadorDTO(
            id=atencion.id,
            request_id=str(atencion.solicitud_id),
            solicitud_nombre=solicitud_nombre,
            cliente_nombre=cliente_nombre,
            scheduled_date=atencion.fecha_programada,
            closing_date=atencion.fecha_fin,
            status=atencion.estado,
            diagnostico_inicial=diagnostico_inicial,
            notas=notas,
            mensaje_bitacora=mensaje_bitacora,
            acciones_disponibles=acciones_disponibles,
        )

        if solicitud_nombre is not None and cliente_nombre is not None:
            try:
                cache.set(key, dto, 30)
            except Exception as exc:
                logger.warning("Cache write error: %s", exc)

        return dto

    @staticmethod
    def obtener_detalle_cliente(
        atention_id: int,
        cliente_id: str,
    ) -> AtencionDetalleClienteDTO:
        key = f"atencion_detalle:cliente:{cliente_id}:{atention_id}"

        try:
            cached_dto = cache.get(key)
            if cached_dto is not None:
                return cached_dto
        except Exception as exc:
            logger.warning("Cache access error: %s", exc)

        try:
            atencion = AtencionRepository.obtener_por_id(atention_id)
        except AtencionNoEncontrada as exc:
            raise AtencionDoesNotExist() from exc
        except DBError as exc:
            logger.error("Database error retrieving attention detail: %s", exc)
            raise AtencionServiceUnavailableError() from exc

        solicitud_dict = AtencionDetalleService._obtener_solicitud_requerida(
            atencion.solicitud_id
        )
        solicitud_cliente_id = str(
            solicitud_dict.get("client_id") or solicitud_dict.get("cliente_id") or ""
        )
        if solicitud_cliente_id != str(cliente_id):
            raise AtencionPermissionDenied()

        try:
            nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atention_id)
            diagnostico_inicial = nota_inicial.content if nota_inicial else None
            notas = NotaSeguimientoRepository.listar_por_atencion(atention_id)
        except DBError as exc:
            logger.error("Database error retrieving attention notes: %s", exc)
            raise AtencionServiceUnavailableError() from exc

        consultores = AtencionDetalleService._obtener_consultores_cliente(
            atencion.consultores
        )
        dto = AtencionDetalleClienteDTO(
            id=atencion.id,
            request_id=str(atencion.solicitud_id),
            solicitud_nombre=solicitud_dict.get("nombre"),
            consultores=consultores,
            scheduled_date=atencion.fecha_programada,
            status=atencion.estado,
            diagnostico_inicial=diagnostico_inicial,
            notas=notas,
            mensaje_bitacora=AtencionDetalleService._mensaje_bitacora_vacia(notas),
        )

        try:
            cache.set(key, dto, 30)
        except Exception as exc:
            logger.warning("Cache write error: %s", exc)

        return dto

    @staticmethod
    def _obtener_solicitud_requerida(solicitud_id: str) -> dict:
        try:
            solicitud_dict = solicitudes_client.get_solicitud(str(solicitud_id))
        except Exception as exc:
            logger.warning("SolicitudesClient request failed: %s", exc)
            raise AtencionServiceUnavailableError() from exc

        if not solicitud_dict:
            raise AtencionServiceUnavailableError()
        return solicitud_dict

    @staticmethod
    def _obtener_consultores_cliente(consultores: list) -> list[ConsultantRefDTO]:
        result = []
        for consultor in consultores:
            try:
                consultor_info = parametrizacion_client.obtener_consultor(
                    str(consultor.id)
                )
            except Exception as exc:
                logger.warning("ParametrizacionClient request failed: %s", exc)
                raise AtencionServiceUnavailableError() from exc

            nombre = (
                consultor_info.nombre
                if consultor_info and consultor_info.nombre
                else consultor.nombre
            )
            result.append(
                ConsultantRefDTO(
                    id=str(consultor.id),
                    name=nombre,
                    is_leader=consultor.es_lider,
                    role=getattr(consultor, "role", "CONSULTOR"),
                )
            )
        return result

    @staticmethod
    def _mensaje_bitacora_vacia(notas: list) -> str | None:
        if not notas:
            return "Esta atención no tiene notas de seguimiento registradas."
        return None

    @staticmethod
    def _calcular_acciones_disponibles(status: str) -> dict[str, bool]:
        if status == "AGENDADA":
            return {"editar": True, "finalizar": True, "cancelar": True}
        return {"editar": False, "finalizar": False, "cancelar": False}

    @staticmethod
    def _obtener_solicitud_info(solicitud_id: str) -> tuple[str | None, str | None]:
        try:
            solicitud_dict = solicitudes_client.get_solicitud(solicitud_id)
            if solicitud_dict:
                return solicitud_dict.get("nombre"), solicitud_dict.get("client_id")
        except Exception as exc:
            logger.warning("SolicitudesClient request failed: %s", exc)
        return None, None

    @staticmethod
    def _obtener_cliente_nombre(client_id: str | None) -> str | None:
        if not client_id:
            return None
        try:
            cliente_dict = clientes_client.get_contacto_cliente(str(client_id))
            if cliente_dict:
                return cliente_dict.get("nombre_completo")
        except Exception as exc:
            logger.warning("ClientesClient request failed: %s", exc)
        return None
