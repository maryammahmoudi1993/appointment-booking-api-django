from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "staff"

router = DefaultRouter()
router.register("staff", views.StaffProfileViewSet, basename="staff-profile")
router.register("working-hours", views.WorkingHoursViewSet, basename="working-hours")
router.register("time-off", views.TimeOffViewSet, basename="time-off")

urlpatterns = [
    path(
        "staff/<int:staff_id>/availability/",
        views.staff_availability,
        name="staff-availability",
    ),
    path("", include(router.urls)),
]
