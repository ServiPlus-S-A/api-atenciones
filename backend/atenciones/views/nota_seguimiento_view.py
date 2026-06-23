import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.constants import ERR_NOTA_SEGUIMIENTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada, SolicitudNoAutorizada
from atenciones.serializers.input.agregar_nota_seguimiento_input_serializer import (
    AgregarNotaSeguimientoInputSerializer,
)
from atenciones.serializers.output.nota_seguimiento_output_serializer import (
    NotaSeguimientoOutputSerializer,
)
from atenciones.services.nota_seguimiento_service import NotaSeguimientoService

logger = logging.getLogger("atenciones.views.nota_seguimiento")


class NotaListCreateView(APIView):
    """
    GET  /api/atenciones/{pk}/notas/  → lista notas de la atención
    POST /api/atenciones/{pk}/notas/  → agrega una nota de seguimiento (HU Consultor)

    Reglas de la HU:
    - El campo contenido es opcional; si no se envía no se guarda nada.
    - Si se envía, debe tener entre 10 y 1000 caracteres.
    - Una vez guardada, la nota es inmutable (solo lectura histórica).
    - Se persiste automáticamente: consultant_id y fecha/hora exacta del registro.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: dict})
    def get(self, request, pk):
        try:
            notes = NotaSeguimientoService.listar(request.user, pk)
        except AtencionNoEncontrada:
            return Response(
                {"detail": "Atención no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            [NotaSeguimientoOutputSerializer.from_dto(n) for n in notes],
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=AgregarNotaSeguimientoInputSerializer, responses={201: dict})
    def post(self, request, pk):
        serializer = AgregarNotaSeguimientoInputSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error": "validation_error",
                    "message": ERR_NOTA_SEGUIMIENTO,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        contenido = serializer.validated_data.get("contenido", "")

        if not contenido:
            return Response(
                {"detail": "No se proporcionó contenido para la nota."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dto = NotaSeguimientoService.agregar_nota(request.user, pk, contenido)
        except AtencionNoEncontrada:
            return Response(
                {"detail": "Atención no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except SolicitudNoAutorizada:
            return Response(
                {"detail": "No tiene permisos para agregar notas a esta atención."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            NotaSeguimientoOutputSerializer.from_dto(dto),
            status=status.HTTP_201_CREATED,
        )