from rest_framework import serializers

from atenciones.dtos.output.atencion_dto import AtencionDTO
from atenciones.dtos.output.consultor_ref_dto import ConsultorRefDTO


class ConsultorRefOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    es_lider = serializers.BooleanField()


class AtencionOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estado = serializers.CharField()
    solicitud_id = serializers.IntegerField()
    fecha_programada = serializers.DateTimeField(allow_null=True)
    fecha_fin = serializers.DateTimeField(allow_null=True)
    consultores = ConsultorRefOutputSerializer(many=True)
    notas_finales = serializers.CharField(allow_null=True)
    fecha_cierre = serializers.DateTimeField(allow_null=True)

    @classmethod
    def from_dto(cls, dto: AtencionDTO) -> dict:
        data = {
            "id": dto.id,
            "estado": dto.estado,
            "solicitud_id": dto.solicitud_id,
            "fecha_programada": dto.fecha_programada,
            "fecha_fin": dto.fecha_fin,
            "consultores": [
                {"id": c.id, "nombre": c.nombre, "es_lider": c.es_lider}
                for c in dto.consultores
            ],
            "notas_finales": dto.notas_finales if dto.estado == "FINALIZADA" else None,
            "fecha_cierre": dto.fecha_cierre,
        }
        return data
