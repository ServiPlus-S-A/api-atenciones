from __future__ import annotations

import logging

from django.db import Error as DBError

from atenciones.dtos.output.atencion_detalle_consultor_dto import (
    MSG_CONTACTO_NO_DISPONIBLE,
    NO_REGISTRADO,
    AtencionDetalleConsultorDTO,
)
from atenciones.dtos.output.nota_seguimiento_dto import MonitoringNoteDTO
from atenciones.exceptions import AtencionDoesNotExist, AtencionServiceUnavailableError
from atenciones.exceptions.custom_exceptions import (
    AtencionNoEncontrada,
    ConsultorNoAsignado,
)
from atenciones.integrations.clientes_client import clientes_client
from atenciones.integrations.solicitudes_client import solicitudes_client
from atenciones.models import AtentionConsultant
from atenciones.repositories.atencion_repository import AtencionRepository
from atenciones.repositories.nota_seguimiento_repository import (
    NotaSeguimientoRepository,
)
from atenciones.services.atencion_detalle_service import AtencionDetalleService

logger = logging.getLogger("atenciones.services.atencion_detalle_consultor")


class AtencionDetalleConsultorService:
    """
    HU-05: Lógica de negocio para que un CONSULTOR obtenga el detalle
    de una atención incluyendo la información de contacto del cliente.
    """

    @staticmethod
    def obtener_detalle_consultor(
        atention_id: int,
        consultant_id: str,
    ) -> AtencionDetalleConsultorDTO:
        """
        Retorna el detalle de la atención enriquecido con los datos de contacto
        del cliente, solo si el consultor está asignado a dicha atención.

        Raises:
            ConsultorNoAsignado: si el consultor no está asignado (CA-3).
            AtencionDoesNotExist: si la atención no existe.
            AtencionServiceUnavailableError: si hay error de base de datos.
        """
        # CA-3: verificar que el consultor está asignado a la atención
        try:
            asignado = AtentionConsultant.objects.filter(
                atention_id=atention_id,
                consultant_id=str(consultant_id),
            ).exists()
        except DBError as exc:
            logger.exception("Database error validating consultant assignment")
            raise AtencionServiceUnavailableError() from exc

        if not asignado:
            raise ConsultorNoAsignado()

        # Obtener atención del repositorio
        try:
            atencion = AtencionRepository.obtener_por_id(atention_id)
        except AtencionNoEncontrada as exc:
            raise AtencionDoesNotExist() from exc
        except DBError as exc:
            logger.exception("Database error retrieving attention for consultor")
            raise AtencionServiceUnavailableError() from exc

        # Obtener notas de seguimiento
        try:
            nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atention_id)
            diagnostico_inicial = nota_inicial.content if nota_inicial else None
            notas: list[MonitoringNoteDTO] = (
                NotaSeguimientoRepository.listar_por_atencion(atention_id)
            )
        except DBError as exc:
            logger.exception("Database error retrieving notes for consultor")
            raise AtencionServiceUnavailableError() from exc

        mensaje_bitacora: str | None = (
            "Esta atención no tiene notas de seguimiento registradas."
            if not notas
            else None
        )

        # CA-2 y CA-4: obtener client_id y solicitud_nombre desde Solicitudes, luego contacto desde Clientes
        contacto_disponible = False
        contacto_error_msg: str | None = MSG_CONTACTO_NO_DISPONIBLE
        contacto_nombre = NO_REGISTRADO
        contacto_telefono = NO_REGISTRADO
        contacto_correo = NO_REGISTRADO
        solicitud_nombre: str | None = None

        try:
            client_id: str | None = None
            solicitud_dict = solicitudes_client.get_solicitud(
                str(atencion.solicitud_id)
            )
            if solicitud_dict:
                client_id = solicitud_dict.get("client_id")
                solicitud_nombre = solicitud_dict.get("nombre")

            if client_id:
                contacto_dict = clientes_client.get_contacto_cliente(str(client_id))
                if contacto_dict is not None:
                    contacto_disponible = True
                    contacto_error_msg = None
                    # CA-5: usar "No registrado" si el campo está ausente o es None
                    contacto_nombre = (
                        contacto_dict.get("nombre_completo") or NO_REGISTRADO
                    )
                    contacto_telefono = contacto_dict.get("telefono") or NO_REGISTRADO
                    contacto_correo = (
                        contacto_dict.get("correo_electronico") or NO_REGISTRADO
                    )
        except Exception as exc:  # noqa: BLE001
            # CA-4: el fallo del servicio externo no interrumpe el resto del detalle
            logger.warning("External service error in consultor service: %s", exc)

        acciones_disponibles = AtencionDetalleService._calcular_acciones_disponibles(
            atencion.estado
        )

        return AtencionDetalleConsultorDTO(
            id=atencion.id,
            request_id=str(atencion.solicitud_id),
            solicitud_nombre=solicitud_nombre,
            scheduled_date=atencion.fecha_programada,
            closing_date=atencion.fecha_fin,
            status=atencion.estado,
            diagnostico_inicial=diagnostico_inicial,
            notas=notas,
            mensaje_bitacora=mensaje_bitacora,
            acciones_disponibles=acciones_disponibles,
            contacto_nombre=contacto_nombre,
            contacto_telefono=contacto_telefono,
            contacto_correo=contacto_correo,
            contacto_disponible=contacto_disponible,
            contacto_error_msg=contacto_error_msg,
        )
