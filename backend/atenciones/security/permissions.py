from rest_framework.permissions import BasePermission

from atenciones.constants import Rol
from atenciones.models import Atencion, AtencionConsultor


def _get_rol(user) -> str | None:
    return getattr(user, "rol", None) or user.groups.filter(name__in=Rol).values_list("name", flat=True).first()


class IsConsultor(BasePermission):
    def has_permission(self, request, view):
        return _get_rol(request.user) == Rol.CONSULTOR


class IsCoordinador(BasePermission):
    def has_permission(self, request, view):
        return _get_rol(request.user) == Rol.COORDINADOR


class IsCliente(BasePermission):
    def has_permission(self, request, view):
        return _get_rol(request.user) == Rol.CLIENTE


class IsOwnerConsultorOrCoordinador(BasePermission):
    def has_object_permission(self, request, view, obj):
        rol = _get_rol(request.user)
        if rol == Rol.COORDINADOR:
            return True
        if rol == Rol.CONSULTOR:
            atencion_id = obj.pk if isinstance(obj, Atencion) else getattr(obj, "atencion_id", obj.pk)
            return AtencionConsultor.objects.filter(
                atention_id=atencion_id,
                consultant_id=request.user.id,
            ).exists()
        return False
