from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("copilot/", views.CopilotView.as_view(), name="copilot"),
    path("admin/copilot/", views.AdminCopilotView.as_view(), name="admin-copilot"),
]
