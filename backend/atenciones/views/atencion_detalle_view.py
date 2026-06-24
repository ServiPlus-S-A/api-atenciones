from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.exceptions import (
    AtencionDoesNotExist,
    AtencionPermissionDenied,
    AtencionServiceUnavailableError,
)
from atenciones.exceptions.custom_exceptions import ConsultorNoAsignado
from atenciones.serializers.output_serializers import (
    AtencionDetalleClienteOutputSerializer,
    AtencionDetalleConsultorOutputSerializer,
    AtencionDetalleCoordinadorOutputSerializer,
)
from atenciones.services.atencion_detalle_service import AtencionDetalleService
from atenciones.services.atencion_detalle_consultor_service import (
    AtencionDetalleConsultorService,
)


class AtencionDetalleView(APIView):
    """
    GET /api/atenciones/{pk}/

    Retorna el detalle completo de una atención según el rol del usuario:
    - COORDINADOR: implementado en HU-19.
    - CONSULTOR:   implementado en HU-05.
    - CLIENTE:     implementado en HU-08.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="atenciones_retrieve",
        responses={
            200: PolymorphicProxySerializer(
                component_name="AtencionDetalleResponse",
                serializers=[
                    AtencionDetalleCoordinadorOutputSerializer,
                    AtencionDetalleConsultorOutputSerializer,
                    AtencionDetalleClienteOutputSerializer,
                ],
                resource_type_field_name=None,
            )
        },
    )
    def get(self, request, pk: int):
        user_id = request.headers.get("X-User-Id")
        user_role = request.headers.get("X-User-Role")

        if not user_id or not user_role:
            return Response(
                {"detail": "Cabeceras de autenticación ausentes."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user_role == "COORDINADOR":
            return self._get_coordinador(pk)

        if user_role == "CONSULTOR":
            return self._get_consultor(pk, user_id)

        if user_role == "CLIENTE":
            return self._get_cliente(pk, user_id)

        return Response(
            {
                "detail": (
                    "No tiene permisos para consultar el detalle de esta atención."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    def _get_coordinador(self, pk: int):
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

    def _get_consultor(self, pk: int, user_id: str):
        try:
            consultor_dto = (
                AtencionDetalleConsultorService.obtener_detalle_consultor(
                    atention_id=pk,
                    consultant_id=user_id,
                )
            )
        except ConsultorNoAsignado:
            return Response(
                {
                    "detail": "No tiene permisos para consultar el detalle de esta atención."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
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

        consultor_serializer = AtencionDetalleConsultorOutputSerializer(
            consultor_dto
        )
        return Response(consultor_serializer.data, status=status.HTTP_200_OK)

    def _get_cliente(self, pk: int, user_id: str):
        try:
            dto = AtencionDetalleService.obtener_detalle_cliente(
                atention_id=pk,
                cliente_id=user_id,
            )
        except AtencionDoesNotExist:
            return Response(
                {"detail": "Atención no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except AtencionPermissionDenied:
            return Response(
                {
                    "detail": (
                        "No tiene permisos para consultar el detalle de esta atención."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
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

        serializer = AtencionDetalleClienteOutputSerializer(dto)
        return Response(serializer.data, status=status.HTTP_200_OK)