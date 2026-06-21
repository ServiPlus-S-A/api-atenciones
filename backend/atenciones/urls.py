from django.urls import path

from atenciones.views.atencion_view import (
    AtencionAnularView,
    AtencionFinalizarView,
    AtencionListCreateView,
    AtencionProgramarView,
)
from atenciones.views.atencion_detalle_view import AtencionDetalleView
from atenciones.views.nota_seguimiento_view import NotaListCreateView

urlpatterns = [
    path("atenciones/", AtencionListCreateView.as_view(), name="atencion-list-create"),
    path("atenciones/<int:pk>/", AtencionDetalleView.as_view(), name="atencion-detail"),
    path(
        "atenciones/<int:pk>/programar/",
        AtencionProgramarView.as_view(),
        name="atencion-programar",
    ),
    path(
        "atenciones/<int:pk>/finalizar/",
        AtencionFinalizarView.as_view(),
        name="atencion-finalizar",
    ),
    path(
        "atenciones/<int:pk>/anular/",
        AtencionAnularView.as_view(),
        name="atencion-anular",
    ),
    path(
        "atenciones/<int:pk>/notas/",
        NotaListCreateView.as_view(),
        name="nota-list-create",
    ),
]
