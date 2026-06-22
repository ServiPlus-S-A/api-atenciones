from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.exceptions import AtencionDoesNotExist, AtencionServiceUnavailableError
from atenciones.serializers.output_serializers import (
    AtencionDetalleCoordinadorOutputSerializer,
)
from atenciones.services.atencion_detalle_service import AtencionDetalleService


class AtencionDetalleView(APIView):
    """
    GET /api/atenciones/{pk}/

    Retorna el detalle completo de una atención.
    Esta tarea (HU-19) solo implementa la rama del rol COORDINADOR.
    Las ramas CONSULTOR y CLIENTE se implementan en HU-05 y HU-08 respectivamente.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="atenciones_retrieve",
        responses={200: AtencionDetalleCoordinadorOutputSerializer},
    )
    def get(self, request, pk: int):
        user_id = request.headers.get("X-User-Id")
        user_role = request.headers.get("X-User-Role")

        if not user_id or not user_role:
            return Response(
                {"detail": "Cabeceras de autenticación ausentes."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user_role != "COORDINADOR":
            # TODO: HU-05/HU-08 implementarán las ramas CONSULTOR y CLIENTE
            return Response(
                {
                    "detail": (
                        "No tiene permisos para consultar el detalle de esta atención."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            dto = AtencionDetalleService.obtener_detalle_coordinador(atention_id=pk)
        except AtencionDoesNotExist:
            return Response(
                {"detail": "Atención no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except AtencionServiceUnavailableError:
            return Response(
                {
                    "detail": (
                        "No fue posible cargar el detalle de la atención. "
                        "Intente de nuevo más tarde."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        serializer = AtencionDetalleCoordinadorOutputSerializer(dto)
        return Response(serializer.data, status=status.HTTP_200_OK)
