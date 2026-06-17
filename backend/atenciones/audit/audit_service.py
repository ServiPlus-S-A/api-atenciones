import hashlib
import json

from atenciones.models import AuditLog


class AuditService:
    """CONCERN-04: registro append-only con hash SHA-256 del payload."""

    @staticmethod
    def _hash_payload(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def registrar(
        cls,
        operation: str,
        actor_id: str | int,
        actor_role: str,
        atention_id: int | None,
        payload: dict,
        jwt_subject: str,
    ) -> AuditLog:
        return AuditLog.objects.create(
            operation=operation,
            actor_id=str(actor_id),
            actor_role=actor_role,
            atention_id=atention_id,
            payload_hash_sha256=cls._hash_payload(payload),
            jwt_subject=jwt_subject,
        )
