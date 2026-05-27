from rest_framework import serializers

from atenciones.dtos.output.nota_seguimiento_dto import NotaSeguimientoDTO


class MonitoringNoteOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    consultant_id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()

    @classmethod
    def from_dto(cls, dto: NotaSeguimientoDTO) -> dict:
        return {
            "id": dto.id,
            "consultant_id": dto.consultant_id,
            "content": dto.content,
            "created_at": dto.created_at,
        }


# Backwards compatibility alias
NotaSeguimientoOutputSerializer = MonitoringNoteOutputSerializer
