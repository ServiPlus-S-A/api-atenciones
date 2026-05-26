from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.filters.atencion_filter import AtencionFilterSet
from atenciones.security.permissions import IsCoordinador, IsConsultor, IsOwnerConsultorOrCoordinador
from atenciones.serializers.input.anular_atencion_input_serializer import AnularAtencionInputSerializer
from atenciones.serializers.input.crear_atencion_input_serializer import CrearAtencionInputSerializer
from atenciones.serializers.input.finalizar_atencion_input_serializer import FinalizarAtencionInputSerializer
from atenciones.serializers.input.listar_atencion_input_serializer import ListarAtencionInputSerializer
from atenciones.serializers.input.programar_atencion_input_serializer import ProgramarAtencionInputSerializer
from atenciones.serializers.output.atencion_output_serializer import AtencionOutputSerializer
from atenciones.services.atencion_service import AtencionService


def _paginate(items: list, page: int, page_size: int) -> dict:
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]
    return {
        "count": len(items),
        "page": page,
        "page_size": page_size,
        "results": [AtencionOutputSerializer.from_dto(d) for d in page_items],
    }


class AtencionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: dict})
    def get(self, request):
        ser = ListarAtencionInputSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        filtros = AtencionFilterSet.parse_query_params(request.query_params)
        filtros = {k: v for k, v in filtros.items() if v is not None}
        items = AtencionService.listar_para_usuario(request.user, filtros)
        return Response(
            _paginate(items, ser.validated_data["page"], ser.validated_data["page_size"]),
        )

    @extend_schema(request=CrearAtencionInputSerializer, responses={201: dict})
    def post(self, request):
        self.permission_classes = [IsAuthenticated, IsCoordinador]
        self.check_permissions(request)
        ser = CrearAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.crear(ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto), status=status.HTTP_201_CREATED)


class AtencionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: dict})
    def get(self, request, pk):
        dto = AtencionService.detalle(pk)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionProgramarView(APIView):
    permission_classes = [IsAuthenticated, IsCoordinador]

    @extend_schema(request=ProgramarAtencionInputSerializer)
    def patch(self, request, pk):
        ser = ProgramarAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.programar(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionFinalizarView(APIView):
    permission_classes = [IsAuthenticated, IsConsultor, IsOwnerConsultorOrCoordinador]

    @extend_schema(request=FinalizarAtencionInputSerializer)
    def patch(self, request, pk):
        ser = FinalizarAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.finalizar(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionAnularView(APIView):
    permission_classes = [IsAuthenticated, IsCoordinador]

    @extend_schema(request=AnularAtencionInputSerializer)
    def patch(self, request, pk):
        ser = AnularAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.anular(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))
