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
        operacion: str,
        actor_id: int,
        actor_rol: str,
        atencion_id: int | None,
        payload: dict,
        jwt_subject: str,
    ) -> AuditLog:
        return AuditLog.objects.create(
            operacion=operacion,
            actor_id=actor_id,
            actor_rol=actor_rol,
            atencion_id=atencion_id,
            payload_hash_sha256=cls._hash_payload(payload),
            jwt_subject=jwt_subject,
        )
