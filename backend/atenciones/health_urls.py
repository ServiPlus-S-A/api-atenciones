from django.urls import path

from atenciones.views.health_view import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
]
