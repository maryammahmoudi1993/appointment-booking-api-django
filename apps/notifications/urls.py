from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "notifications"

router = DefaultRouter()
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register(
    "webhook-subscriptions",
    views.WebhookSubscriptionViewSet,
    basename="webhook-subscription",
)
router.register(
    "webhook-deliveries", views.WebhookDeliveryViewSet, basename="webhook-delivery"
)

urlpatterns = [
    path("", include(router.urls)),
]
