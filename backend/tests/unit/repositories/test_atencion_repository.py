import pytest

from atenciones.constants import EstadoAtencion, Rol
from atenciones.repositories.atencion_repository import AtencionRepository
from tests.factories.atencion_factory import AtencionAnuladaFactory, AtencionFactory


@pytest.mark.django_db
def test_listar_excluye_anulada_para_consultor():
    AtencionFactory()
    AtencionAnuladaFactory()
    result = AtencionRepository.listar({}, estados_excluidos=[EstadoAtencion.ANULADA])
    assert all(d.estado != EstadoAtencion.ANULADA for d in result)


@pytest.mark.django_db
def test_listar_incluye_anulada_para_coordinador():
    AtencionAnuladaFactory()
    result = AtencionRepository.listar({}, estados_excluidos=None)
    assert any(d.estado == EstadoAtencion.ANULADA for d in result)


@pytest.mark.django_db
def test_guardar_retorna_dto_no_model():
    from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO

    dto = AtencionRepository.guardar(
        CrearAtencionInputDTO(
            solicitud_id=99,
            consultor_ids=[1],
            mensaje_preliminar="Mensaje preliminar válido.",
            creado_por_id=1,
        ),
    )
    assert hasattr(dto, "id")
    assert dto.estado == EstadoAtencion.AGENDADA
