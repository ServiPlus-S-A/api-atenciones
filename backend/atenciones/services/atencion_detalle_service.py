import logging

from django.core.cache import cache
from django.db import Error as DBError

from atenciones.dtos.output.atencion_detalle_coordinador_dto import AtencionDetalleCoordinadorDTO
from atenciones.exceptions import AtencionDoesNotExist, AtencionServiceUnavailableError
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
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
            logger.error("Database error retrieving attention detail: %s", exc)
            raise AtencionServiceUnavailableError() from exc

        try:
            nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atention_id)
            diagnostico_inicial = nota_inicial.content if nota_inicial else None
            notas = NotaSeguimientoRepository.listar_por_atencion(atention_id)
        except DBError as exc:
            logger.error("Database error retrieving attention notes: %s", exc)
            raise AtencionServiceUnavailableError() from exc

        mensaje_bitacora = AtencionDetalleService._mensaje_bitacora_vacia(notas)

        solicitud_nombre = None
        client_id = None
        try:
            solicitud_dict = solicitudes_client.get_solicitud(
                str(atencion.solicitud_id)
            )
            if solicitud_dict:
                solicitud_nombre = solicitud_dict.get("nombre")
                client_id = solicitud_dict.get("client_id")
        except Exception as exc:
            logger.warning("SolicitudesClient request failed: %s", exc)

        cliente_nombre = None
        if client_id:
            try:
                cliente_dict = clientes_client.get_contacto_cliente(str(client_id))
                if cliente_dict:
                    cliente_nombre = cliente_dict.get("nombre_completo")
            except Exception as exc:
                logger.warning("ClientesClient request failed: %s", exc)

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
    def _mensaje_bitacora_vacia(notas: list) -> str | None:
        if not notas:
            return "Esta atención no tiene notas de seguimiento registradas."
        return None

    @staticmethod
    def _calcular_acciones_disponibles(status: str) -> dict[str, bool]:
        if status == "AGENDADA":
            return {"editar": True, "finalizar": True, "cancelar": True}
        return {"editar": False, "finalizar": False, "cancelar": False}
