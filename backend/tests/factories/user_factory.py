import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class ConsultorFactory(UserFactory):
    rol = "CONSULTOR"


class CoordinadorFactory(UserFactory):
    rol = "COORDINADOR"


class ClienteFactory(UserFactory):
    rol = "CLIENTE"
