import pytest
from freezegun import freeze_time

from atenciones.models import NotaSeguimiento
from atenciones.repositories.nota_seguimiento_repository import (
    NotaSeguimientoRepository,
)
from tests.factories import AtencionFactory


@pytest.mark.django_db
@pytest.mark.unit
def test_obtener_nota_inicial_retorna_la_mas_antigua():
    atencion = AtencionFactory()

    with freeze_time("2026-06-20T10:00:00Z"):
        nota1 = NotaSeguimiento.objects.create(
            atention=atencion, consultant_id="1", content="Nota 1"
        )
    with freeze_time("2026-06-20T11:00:00Z"):
        NotaSeguimiento.objects.create(
            atention=atencion, consultant_id="1", content="Nota 2"
        )
    with freeze_time("2026-06-20T12:00:00Z"):
        NotaSeguimiento.objects.create(
            atention=atencion, consultant_id="1", content="Nota 3"
        )

    nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atencion.id)
    assert nota_inicial is not None
    assert nota_inicial.id == nota1.id
    assert nota_inicial.content == "Nota 1"


@pytest.mark.django_db
@pytest.mark.unit
def test_obtener_nota_inicial_sin_notas_retorna_none():
    atencion = AtencionFactory()
    nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atencion.id)
    assert nota_inicial is None


@pytest.mark.django_db
@pytest.mark.unit
def test_obtener_nota_inicial_no_mezcla_atenciones():
    atencion1 = AtencionFactory()
    atencion2 = AtencionFactory()

    nota1 = NotaSeguimiento.objects.create(
        atention=atencion1, consultant_id="1", content="Nota Atencion 1"
    )
    _ = NotaSeguimiento.objects.create(
        atention=atencion2, consultant_id="1", content="Nota Atencion 2"
    )

    nota_inicial = NotaSeguimientoRepository.obtener_nota_inicial(atencion1.id)
    assert nota_inicial is not None
    assert nota_inicial.id == nota1.id
    assert nota_inicial.content == "Nota Atencion 1"
