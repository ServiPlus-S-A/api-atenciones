from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

from atenciones.exceptions.custom_exceptions import BaseAtencionException
from atenciones.security.secure_logger import SecureLogger


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, BaseAtencionException):
        SecureLogger.registrar_fallo(
            operation="exception",
            actor_id=getattr(context.get("request"), "user", None),
            detail=str(exc.detail),
            context=context,
        )
        return _build_response(
            code=getattr(exc, "default_code", "error"),
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    if isinstance(exc, ValidationError):
        field_errors = exc.detail if isinstance(exc.detail, dict) else {"non_field_errors": exc.detail}
        return _build_response(
            code="validation_error",
            message="Error de validación.",
            status_code=400,
            field_errors=field_errors,
        )

    if response is not None and response.data:
        SecureLogger.registrar_fallo(
            operation="exception",
            actor_id=getattr(context.get("request"), "user", None),
            detail=str(response.data),
            context=context,
        )

    return response


def _build_response(code, message, status_code, field_errors=None):
    from rest_framework.response import Response

    body = {"error": code, "message": message}
    if field_errors:
        body["field_errors"] = field_errors
    return Response(body, status=status_code)
