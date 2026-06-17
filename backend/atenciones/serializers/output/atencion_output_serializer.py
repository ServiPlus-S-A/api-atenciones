from rest_framework import serializers

from atenciones.dtos.output.atencion_dto import AtencionDTO


class ConsultorRefOutputSerializer(serializers.Serializer):
    id = serializers.CharField()
    nombre = serializers.CharField()
    es_lider = serializers.BooleanField()

    # English fields (HU-02)
    name = serializers.CharField()
    is_leader = serializers.BooleanField()
    role = serializers.CharField()


class AtencionOutputSerializer(serializers.Serializer):
    # Spanish keys (Backward compatibility)
    id = serializers.IntegerField()
    estado = serializers.CharField()
    solicitud_id = serializers.CharField()
    fecha_programada = serializers.DateTimeField(allow_null=True)
    fecha_fin = serializers.DateTimeField(allow_null=True)
    consultores = ConsultorRefOutputSerializer(many=True)
    notas_finales = serializers.CharField(allow_null=True)
    fecha_cierre = serializers.DateTimeField(allow_null=True)

    # English keys (HU-02)
    status = serializers.CharField()
    request_id = serializers.CharField()
    scheduled_date = serializers.DateTimeField(allow_null=True)
    closing_date = serializers.DateTimeField(allow_null=True)
    consultants = ConsultorRefOutputSerializer(many=True)
    final_note = serializers.CharField(allow_null=True)
    cancellation_reason = serializers.CharField(allow_null=True)

    @classmethod
    def from_dto(cls, dto: AtencionDTO) -> dict:
        try:
            solicitud_id_val = int(dto.solicitud_id)
        except (ValueError, TypeError):
            solicitud_id_val = str(dto.solicitud_id)

        consultants_data = []
        consultores_data = []
        for c in dto.consultores:
            try:
                cid_val = int(c.id)
            except (ValueError, TypeError):
                cid_val = str(c.id)

            consultants_data.append(
                {
                    "id": str(c.id),
                    "name": c.nombre,
                    "is_leader": c.es_lider,
                    "role": getattr(c, "role", "CONSULTOR"),
                }
            )

            consultores_data.append(
                {
                    "id": cid_val,
                    "nombre": c.nombre,
                    "es_lider": c.es_lider,
                }
            )

        data = {
            # Spanish keys (Backward compatibility)
            "id": dto.id,
            "estado": dto.estado,
            "solicitud_id": solicitud_id_val,
            "fecha_programada": dto.fecha_programada,
            "fecha_fin": dto.fecha_fin,
            "consultores": consultores_data,
            "notas_finales": dto.notas_finales if dto.estado == "FINALIZADA" else None,
            "fecha_cierre": dto.fecha_cierre,
            # English keys (HU-02)
            "status": dto.estado,
            "request_id": str(dto.solicitud_id),
            "scheduled_date": dto.fecha_programada,
            "closing_date": dto.fecha_fin,
            "consultants": consultants_data,
            "final_note": dto.notas_finales if dto.estado == "FINALIZADA" else None,
            "cancellation_reason": dto.motivo_anulacion,
        }
        return data
