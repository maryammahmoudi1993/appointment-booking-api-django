from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "appointments"

router = DefaultRouter()
router.register("appointments", views.AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
]
