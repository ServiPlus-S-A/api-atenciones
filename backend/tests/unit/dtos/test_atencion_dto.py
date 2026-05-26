import pytest

from atenciones.dtos.output.atencion_dto import AtencionDTO
from tests.factories.atencion_factory import AtencionFactory


@pytest.mark.django_db
@pytest.mark.unit
def test_from_orm_no_expone_campos_sensibles():
    atencion = AtencionFactory()
    dto = AtencionDTO.from_orm(atencion)
    assert not hasattr(dto, "creado_por_id")


@pytest.mark.unit
def test_dto_es_inmutable():
    dto = AtencionDTO(
        id=1,
        estado="AGENDADA",
        solicitud_id=1,
        fecha_programada=None,
        fecha_fin=None,
        notas_finales=None,
        fecha_cierre=None,
        consultores=[],
    )
    with pytest.raises(Exception):
        dto.estado = "FINALIZADA"
