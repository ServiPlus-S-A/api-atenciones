from rest_framework import serializers

from atenciones.dtos.output.atencion_dto import AtencionDTO


class ConsultantRefOutputSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    is_leader = serializers.BooleanField()
    role = serializers.CharField()


class AtencionOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    request_id = serializers.CharField()
    scheduled_date = serializers.DateTimeField(allow_null=True)
    closing_date = serializers.DateTimeField(allow_null=True)
    consultants = ConsultantRefOutputSerializer(many=True)
    final_note = serializers.CharField(allow_null=True)
    cancellation_reason = serializers.CharField(allow_null=True)
    customer_name = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()

    @classmethod
    def from_dto(cls, dto: AtencionDTO) -> dict:
        consultants_data = []
        for c in dto.consultores:
            consultants_data.append(
                {
                    "id": str(c.id),
                    "name": c.nombre,
                    "is_leader": c.es_lider,
                    "role": getattr(c, "role", "CONSULTOR"),
                }
            )

        data = {
            "id": dto.id,
            "status": dto.estado,
            "request_id": str(dto.solicitud_id),
            "scheduled_date": dto.fecha_programada,
            "closing_date": dto.fecha_fin,
            "consultants": consultants_data,
            "final_note": dto.notas_finales if dto.estado == "FINALIZADA" else None,
            "cancellation_reason": dto.motivo_anulacion,
            "customer_name": dto.cliente_nombre,
            "created_at": dto.fecha_registro,
        }
        return data
