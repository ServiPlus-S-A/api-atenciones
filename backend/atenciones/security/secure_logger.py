import hashlib
import json
import logging

from atenciones.models import AuditLog

logger = logging.getLogger("atenciones.secure")


class SecureLogger:
    """Secure Logger — append-only vía AuditLog; sin UPDATE/DELETE."""

    @staticmethod
    def registrar(
        operacion: str,
        actor_id: int,
        actor_rol: str,
        recurso_id: int | None,
        ip_origen: str,
        jwt_subject: str,
        payload: dict | None = None,
    ) -> None:
        payload = payload or {}
        canonical = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        AuditLog.objects.create(
            operacion=operacion,
            actor_id=actor_id or 0,
            actor_rol=actor_rol or "SYSTEM",
            atencion_id=recurso_id,
            payload_hash_sha256=payload_hash,
            jwt_subject=jwt_subject or "anonymous",
        )
        logger.info(
            "audit operacion=%s actor=%s recurso=%s ip=%s",
            operacion,
            actor_id,
            recurso_id,
            ip_origen,
        )

    @staticmethod
    def registrar_fallo(operacion: str, actor_id, detalle: str, context: dict) -> None:
        logger.warning("fallo operacion=%s detalle=%s", operacion, detalle)
