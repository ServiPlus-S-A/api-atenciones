from rest_framework import serializers

from atenciones.dtos.output.nota_seguimiento_dto import NotaSeguimientoDTO


class NotaSeguimientoOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    consultor_id = serializers.IntegerField()
    contenido = serializers.CharField()
    timestamp = serializers.DateTimeField()

    @classmethod
    def from_dto(cls, dto: NotaSeguimientoDTO) -> dict:
        return {
            "id": dto.id,
            "consultor_id": dto.consultor_id,
            "contenido": dto.contenido,
            "timestamp": dto.timestamp,
        }
