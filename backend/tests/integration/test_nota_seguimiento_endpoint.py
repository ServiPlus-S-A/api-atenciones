"""
Tests de integración - HU Consultor: Agregar nota de seguimiento
Endpoint: POST /api/atenciones/{pk}/notas/
"""
import pytest
from django.urls import reverse

from atenciones.models import NotaSeguimiento
from tests.factories.atencion_factory import AtencionFactory

# CA-1: Guardar nota válida


@pytest.mark.django_db
@pytest.mark.integration
def test_agregar_nota_exitosa_retorna_201(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "Nota con contenido suficiente."}, format="json"
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Nota con contenido suficiente."
    assert "created_at" in data
    assert "id" in data


@pytest.mark.django_db
@pytest.mark.integration
def test_agregar_nota_persiste_consultant_id_automaticamente(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})
    user = api_client_consultor.test_user

    api_client_consultor.post(
        url, {"contenido": "Hallazgo encontrado durante la visita."}, format="json"
    )

    nota = NotaSeguimiento.objects.get(atention=atencion)
    assert str(nota.consultant_id) == str(user.id)


@pytest.mark.django_db
@pytest.mark.integration
def test_agregar_nota_persiste_fecha_hora_automaticamente(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    api_client_consultor.post(
        url, {"contenido": "Dificultad encontrada en el proceso."}, format="json"
    )

    nota = NotaSeguimiento.objects.get(atention=atencion)
    assert nota.created_at is not None


# CA-2: Validación de longitud mínima (10 caracteres)


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_menor_a_10_caracteres_retorna_400(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "abc"}, format="json"
    )

    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "La nota debe tener entre 10 y 1000 caracteres."


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_exactamente_9_caracteres_retorna_400(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "123456789"}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["message"] == "La nota debe tener entre 10 y 1000 caracteres."


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_exactamente_10_caracteres_es_valida(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "1234567890"}, format="json"
    )

    assert response.status_code == 201


# CA-3: Validación de longitud máxima (1000 caracteres)


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_mayor_a_1000_caracteres_retorna_400(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "x" * 1001}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["message"] == "La nota debe tener entre 10 y 1000 caracteres."


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_exactamente_1000_caracteres_es_valida(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(
        url, {"contenido": "a" * 1000}, format="json"
    )

    assert response.status_code == 201


# CA-4: Nota no guardada si validación falla


@pytest.mark.django_db
@pytest.mark.integration
def test_nota_invalida_no_se_persiste_en_bd(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    api_client_consultor.post(url, {"contenido": "corta"}, format="json")

    assert not NotaSeguimiento.objects.filter(atention=atencion).exists()


# CA-5: Campo opcional — sin contenido no guarda


@pytest.mark.django_db
@pytest.mark.integration
def test_post_sin_contenido_retorna_400(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(url, {}, format="json")

    assert response.status_code == 400
    assert not NotaSeguimiento.objects.filter(atention=atencion).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_post_contenido_vacio_retorna_400(api_client_consultor):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.post(url, {"contenido": "   "}, format="json")

    assert response.status_code == 400


# CA-6: Inmutabilidad — nota guardada no puede modificarse

@pytest.mark.django_db
@pytest.mark.integration
def test_nota_guardada_es_inmutable(api_client_consultor):
    atencion = AtencionFactory()
    nota = NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id=str(api_client_consultor.test_user.id),
        content="Nota original guardada.",
    )

    with pytest.raises(ValueError, match="immutable"):
        nota.content = "Intento de modificación."
        nota.save()


# CA-7: Control de acceso — solo consultor y coordinador

@pytest.mark.django_db
@pytest.mark.integration
def test_cliente_no_puede_agregar_nota(api_client_cliente):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_cliente.post(
        url, {"contenido": "Nota de un cliente no autorizado."}, format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.integration
def test_coordinador_puede_agregar_nota(api_client_coordinador):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_coordinador.post(
        url, {"contenido": "Nota agregada por el coordinador."}, format="json"
    )

    assert response.status_code == 201


@pytest.mark.django_db
@pytest.mark.integration
def test_sin_autenticacion_retorna_401(client):
    atencion = AtencionFactory()
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = client.post(url, {"contenido": "Nota sin autenticar."}, format="json")

    assert response.status_code == 401


# CA-8: Atención inexistente

@pytest.mark.django_db
@pytest.mark.integration
def test_atencion_inexistente_retorna_404(api_client_consultor):
    url = reverse("nota-list-create", kwargs={"pk": 99999})

    response = api_client_consultor.post(
        url, {"contenido": "Nota para atención que no existe."}, format="json"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Atención no encontrada."


# CA-9: GET — listar notas

@pytest.mark.django_db
@pytest.mark.integration
def test_listar_notas_retorna_200(api_client_consultor):
    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id=str(user.id),
        content="Primera nota de seguimiento.",
    )
    url = reverse("nota-list-create", kwargs={"pk": atencion.pk})

    response = api_client_consultor.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Primera nota de seguimiento."