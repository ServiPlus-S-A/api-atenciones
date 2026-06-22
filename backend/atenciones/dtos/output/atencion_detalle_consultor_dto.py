from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from atenciones.dtos.output.nota_seguimiento_dto import MonitoringNoteDTO

# Texto centinela para campos de contacto sin valor registrado (CA-5)
NO_REGISTRADO = "No registrado"

# Mensaje cuando el servicio de Clientes no responde a tiempo (CA-4)
MSG_CONTACTO_NO_DISPONIBLE = (
    "Información de contacto no disponible temporalmente. "
    "Intente de nuevo más tarde"
)


@dataclass(frozen=True)
class AtencionDetalleConsultorDTO:
    """
    HU-05: DTO de solo lectura para el rol CONSULTOR.

    Incluye los campos de contacto del cliente recuperados desde el módulo
    de Clientes. Si el servicio no está disponible, `contacto_disponible`
    será False y `contacto_error_msg` contendrá el mensaje de degradación.
    Los campos de contacto nunca se omiten: usan "No registrado" cuando
    el valor no está registrado en el módulo de Clientes (CA-5).
    """

    id: int
    request_id: str
    solicitud_nombre: str | None
    scheduled_date: datetime | None
    closing_date: datetime | None
    status: str
    diagnostico_inicial: str | None
    notas: list[MonitoringNoteDTO]
    mensaje_bitacora: str | None
    acciones_disponibles: dict[str, bool]

    # Campos de contacto del cliente (CA-2)
    contacto_nombre: str          # "No registrado" si ausente
    contacto_telefono: str        # "No registrado" si ausente
    contacto_correo: str          # "No registrado" si ausente
    contacto_disponible: bool     # False si el servicio de Clientes falló
    contacto_error_msg: str | None  # Mensaje de CA-4 cuando contacto_disponible=False
