from types import SimpleNamespace

import pytest

from atenciones.constants import Rol
from atenciones.exceptions.custom_exceptions import SolicitudNoAutorizada
from atenciones.models import NotaSeguimiento
from atenciones.services.nota_seguimiento_service import NotaSeguimientoService
from tests.factories.atencion_factory import AtencionFactory


def _user(user_id=99, rol=Rol.CONSULTOR):
    return SimpleNamespace(id=user_id, rol=rol, username=f"user-{user_id}")


@pytest.mark.django_db
def test_agregar_nota_crea_registro_y_auditoria():
    atencion = AtencionFactory()
    user = _user()

    dto = NotaSeguimientoService.agregar_nota(
        user,
        atencion.pk,
        "Nota inicial con suficiente detalle.",
    )

    assert dto.id is not None
    assert dto.consultant_id == user.id
    assert dto.content == "Nota inicial con suficiente detalle."
    assert NotaSeguimiento.objects.filter(
        atention=atencion, content=dto.content
    ).exists()


@pytest.mark.django_db
def test_agregar_nota_rechaza_roles_no_autorizados():
    atencion = AtencionFactory()

    with pytest.raises(SolicitudNoAutorizada):
        NotaSeguimientoService.agregar_nota(
            _user(rol=Rol.CLIENTE),
            atencion.pk,
            "Nota que no debe guardarse.",
        )


@pytest.mark.django_db
def test_listar_filtra_por_consultor_cuando_usuario_es_consultor():
    atencion = AtencionFactory()
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="10",
        content="Nota visible para consultor 10.",
    )
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="20",
        content="Nota de otro consultor.",
    )

    result = NotaSeguimientoService.listar(_user(user_id=10), atencion.pk)

    assert [nota.content for nota in result] == ["Nota visible para consultor 10."]


@pytest.mark.django_db
def test_listar_coordinador_ve_todas_las_notas():
    atencion = AtencionFactory()
    NotaSeguimiento.objects.create(atention=atencion, consultant_id="10", content="Uno")
    NotaSeguimiento.objects.create(atention=atencion, consultant_id="20", content="Dos")

    result = NotaSeguimientoService.listar(_user(rol=Rol.COORDINADOR), atencion.pk)

    assert {nota.content for nota in result} == {"Uno", "Dos"}
