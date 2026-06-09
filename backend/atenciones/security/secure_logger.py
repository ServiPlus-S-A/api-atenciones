import hashlib
import json
import logging

from atenciones.models import AuditLog

logger = logging.getLogger("atenciones.secure")


class SecureLogger:
    """Secure Logger — append-only via AuditLog; no UPDATE/DELETE."""

    @staticmethod
    def registrar(
        operation: str,
        actor_id: int,
        actor_role: str,
        resource_id: int | None,
        ip_origin: str,
        jwt_subject: str,
        payload: dict | None = None,
    ) -> None:
        payload = payload or {}
        canonical = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        AuditLog.objects.create(
            operation=operation,
            actor_id=actor_id or 0,
            actor_role=actor_role or "SYSTEM",
            atention_id=resource_id,
            payload_hash_sha256=payload_hash,
            jwt_subject=jwt_subject or "anonymous",
        )
        logger.info(
            "audit operation=%s actor=%s resource=%s ip=%s",
            operation,
            actor_id,
            resource_id,
            ip_origin,
        )

    @staticmethod
    def registrar_fallo(operation: str, actor_id, detail: str, context: dict) -> None:
        logger.warning("failure operation=%s detail=%s", operation, detail)
