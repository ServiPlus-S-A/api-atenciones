from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.serializers.output.nota_seguimiento_output_serializer import NotaSeguimientoOutputSerializer
from atenciones.services.nota_seguimiento_service import NotaSeguimientoService


class NotaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: dict})
    def get(self, request, pk):
        notas = NotaSeguimientoService.listar(request.user, pk)
        return Response([NotaSeguimientoOutputSerializer.from_dto(n) for n in notas])

    @extend_schema(request=dict, responses={201: dict})
    def post(self, request, pk):
        contenido = request.data.get("contenido", "")
        if len(contenido) < 15:
            return Response(
                {"error": "validation_error", "message": "contenido mínimo 15 caracteres"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dto = NotaSeguimientoService.agregar_nota(request.user, pk, contenido)
        return Response(
            NotaSeguimientoOutputSerializer.from_dto(dto),
            status=status.HTTP_201_CREATED,
        )
