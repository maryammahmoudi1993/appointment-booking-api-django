from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

admin.site.site_header = "Booking System Admin"
admin.site.site_title = "Booking Admin Portal"
admin.site.index_title = "Manage Bookings"

api_urlpatterns = [
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.services.urls")),
    path("api/", include("apps.staff.urls")),
    path("api/", include("apps.appointments.urls")),
    path("api/", include("apps.engagement.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    *api_urlpatterns,
]

# SPA catch-all: serve index.html for any non-API, non-admin path
urlpatterns += [
    re_path(r"^(?!api/|admin/).*$", TemplateView.as_view(template_name="index.html")),
]
