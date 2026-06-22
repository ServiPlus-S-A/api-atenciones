from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atenciones.filters.atencion_filter import AtencionFilterForm
from atenciones.security.permissions import (
    IsCoordinador,
    IsConsultor,
    IsOwnerConsultorOrCoordinador,
)
from atenciones.serializers.input.anular_atencion_input_serializer import (
    AnularAtencionInputSerializer,
)
from atenciones.serializers.input.crear_atencion_input_serializer import (
    CrearAtencionInputSerializer,
)
from atenciones.serializers.input.finalizar_atencion_input_serializer import (
    FinalizarAtencionInputSerializer,
)
from atenciones.serializers.input.listar_atencion_input_serializer import (
    ListarAtencionInputSerializer,
)
from atenciones.serializers.input.programar_atencion_input_serializer import (
    ProgramarAtencionInputSerializer,
)
from atenciones.serializers.input.verificar_cruce_input_serializer import (
    VerificarCruceInputSerializer,
)
from atenciones.serializers.output.atencion_output_serializer import (
    AtencionOutputSerializer,
)
from atenciones.services.atencion_service import AtencionService
from atenciones.models import Atention
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.repositories.atencion_repository import AtencionRepository


def _get_mock_user(user_id, rol="CONSULTOR"):
    from django.conf import settings

    mock_responses = getattr(settings, "PARAMETRIZACION_MOCK_RESPONSES", None)
    if mock_responses:
        user_mock = mock_responses.get(str(user_id))
        user_mock.rol = rol
        user_mock.is_authenticated = True
        return user_mock

    # Fallback para entornos de testing/producción si no está definido el mock dict
    class FallbackMockUser:
        def __init__(self, id, rol):
            self.id = str(id)
            self.rol = rol
            self.is_authenticated = True

    return FallbackMockUser(user_id, rol)


def _mock_user_if_unauthenticated(
    drf_request,
    pk=None,
    default_id="1",
    default_rol="CONSULTOR",
    query_atencion_id=None,
    query_consultor_id=None,
):
    if drf_request.user and drf_request.user.is_authenticated:
        return

    # Caso 1: Buscar consultor asignado en la atención si se tiene el PK de la URL
    if pk:
        try:
            atencion_obj = Atention.objects.get(pk=pk)
            from atenciones.models import AtentionConsultant

            first = AtentionConsultant.objects.filter(atention=atencion_obj).first()
            mock_id = first.consultant_id if first else default_id
            drf_request.user = _get_mock_user(mock_id, default_rol)
            return
        except Atention.DoesNotExist:
            pass

    # Caso 2: Verificar cruces por query params
    if query_atencion_id or query_consultor_id:
        mock_id = default_id
        if query_atencion_id:
            try:
                atencion = Atention.objects.get(pk=query_atencion_id)
                first = atencion.consultants_rel.first()
                if first:
                    mock_id = first.consultant_id
            except Atention.DoesNotExist:
                pass
        elif query_consultor_id:
            mock_id = query_consultor_id
        drf_request.user = _get_mock_user(mock_id, default_rol)
        return

    # Caso 3: Fallback a mock estático
    drf_request.user = _get_mock_user(default_id, default_rol)


def _paginate(items: list, page: int, page_size: int) -> dict:
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]
    count = len(items)
    total_pages = (count + page_size - 1) // page_size if count else 0
    return {
        "count": count,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size,
        "results": [AtencionOutputSerializer.from_dto(d) for d in page_items],
    }


class AtencionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(drf_request, default_id="1", default_rol="CONSULTOR")
        return drf_request

    @extend_schema(operation_id="atenciones_list", responses={200: dict})
    def get(self, request):
        ser = ListarAtencionInputSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        filtros = AtencionFilterForm.parse_query_params(request.query_params)
        filtros = {k: v for k, v in filtros.items() if v is not None}
        items = AtencionService.listar_para_usuario(request.user, filtros)
        return Response(
            _paginate(
                items, ser.validated_data["page"], ser.validated_data["page_size"]
            ),
        )

    @extend_schema(request=CrearAtencionInputSerializer, responses={201: dict})
    def post(self, request):
        ser = CrearAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.crear(ser.validated_data, request.user)
        return Response(
            AtencionOutputSerializer.from_dto(dto), status=status.HTTP_201_CREATED
        )


class AtencionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(drf_request, default_id="1", default_rol="CONSULTOR")
        return drf_request

    @extend_schema(
        operation_id="atenciones_retrieve", responses={200: AtencionOutputSerializer}
    )
    def get(self, request, pk):
        dto = AtencionService.detalle(pk)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionProgramarView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerConsultorOrCoordinador]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(drf_request, pk=kwargs.get("pk"), default_id="1", default_rol="CONSULTOR")
        return drf_request

    @extend_schema(
        summary="Programar/Reagendar fecha y hora de atención",
        description=(
            "Permite a un consultor asignado a la atención o a un coordinador programar o reagendar "
            "la fecha y hora de inicio, así como la fecha estimada de finalización. Ambos campos son obligatorios "
            "y deben ser bloques de 30 minutos (por ejemplo, minutos :00 o :30, y segundos/microsegundos en 0). "
            "Las fechas no pueden estar en el pasado relativo a la fecha del servidor, y se verifican cruces "
            "de horario para todos los consultores asignados a esta atención."
        ),
        request=ProgramarAtencionInputSerializer,
        responses={200: AtencionOutputSerializer},
        examples=[
            OpenApiExample(
                "Ejemplo de Programación Válida",
                description="Ejemplo con fechas futuras válidas alineadas a bloques de 30 minutos, donde la fecha de fin es posterior.",
                value={
                    "fecha_programada": "2026-06-20T10:00:00Z",
                    "fecha_fin": "2026-06-20T11:00:00Z",
                },
                request_only=True,
            )
        ],
    )
    def patch(self, request, pk):
        try:
            atencion_obj = Atention.objects.get(pk=pk)
        except Atention.DoesNotExist:
            raise AtencionNoEncontrada()
        self.check_object_permissions(request, atencion_obj)

        ser = ProgramarAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.programar(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionFinalizarView(APIView):
    permission_classes = [IsAuthenticated, IsConsultor, IsOwnerConsultorOrCoordinador]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(drf_request, pk=kwargs.get("pk"), default_id="1", default_rol="CONSULTOR")
        return drf_request

    @extend_schema(
        request=FinalizarAtencionInputSerializer,
        responses={200: AtencionOutputSerializer},
    )
    def patch(self, request, pk):
        try:
            atencion_obj = Atention.objects.get(pk=pk)
        except Atention.DoesNotExist:
            raise AtencionNoEncontrada()
        self.check_object_permissions(request, atencion_obj)

        ser = FinalizarAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.finalizar(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionAnularView(APIView):
    permission_classes = [IsAuthenticated, IsCoordinador]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(drf_request, default_id="1", default_rol="COORDINADOR")
        return drf_request

    @extend_schema(
        request=AnularAtencionInputSerializer, responses={200: AtencionOutputSerializer}
    )
    def patch(self, request, pk):
        ser = AnularAtencionInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = AtencionService.anular(pk, ser.validated_data, request.user)
        return Response(AtencionOutputSerializer.from_dto(dto))


class AtencionVerificarCruceView(APIView):
    permission_classes = [IsAuthenticated]

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        _mock_user_if_unauthenticated(
            drf_request,
            query_atencion_id=drf_request.query_params.get("atencion_id"),
            query_consultor_id=drf_request.query_params.get("consultor_id"),
            default_id="1",
            default_rol="CONSULTOR",
        )
        return drf_request

    @extend_schema(
        parameters=[VerificarCruceInputSerializer],
        responses={200: dict},
    )
    def get(self, request):
        ser = VerificarCruceInputSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)

        fecha_inicio = ser.validated_data["fecha_inicio"]
        fecha_fin = ser.validated_data["fecha_fin"]
        consultor_id = ser.validated_data.get("consultor_id")
        atencion_id = ser.validated_data.get("atencion_id")

        if atencion_id:
            try:
                atencion = Atention.objects.get(pk=atencion_id)
                consultor_ids = [
                    rel.consultant_id for rel in atencion.consultants_rel.all()
                ]
            except Atention.DoesNotExist:
                raise AtencionNoEncontrada()
        else:
            if not consultor_id:
                if request.user and request.user.is_authenticated:
                    consultor_id = str(request.user.id)
                else:
                    consultor_id = "1"
            consultor_ids = [consultor_id]

        cruces = AtencionRepository.buscar_cruces(
            consultor_ids=consultor_ids,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            excluir_atencion_id=atencion_id,
        )

        if cruces:
            return Response(
                {
                    "cruce": True,
                    "mensaje": "Ya tienes una atención programada en este horario. Por favor selecciona otro.",
                    "cruces": [
                        {
                            "consultor_id": cid,
                            "fecha_inicio": start.isoformat(),
                            "fecha_fin": end.isoformat(),
                        }
                        for cid, start, end in cruces
                    ],
                }
            )

        return Response({"cruce": False})
