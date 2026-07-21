from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from core.mixins import BusinessScopedMixin
from core.permissions import IsAdminRole

from .models import Notification, WebhookDelivery, WebhookSubscription
from .serializers import (
    NotificationSerializer,
    WebhookDeliverySerializer,
    WebhookSubscriptionSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Notifications"],
        summary="List notifications",
        description="Admin only. Business-scoped notification history.",
    ),
)
class NotificationViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("recipient", "business")
    serializer_class = NotificationSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = [IsAdminRole]


@extend_schema_view(
    list=extend_schema(
        tags=["Webhooks"],
        summary="List webhook subscriptions",
        description="Admin only. Business-scoped webhook subscriptions.",
    ),
    create=extend_schema(
        tags=["Webhooks"],
        summary="Create a webhook subscription",
        description="Admin only. Register a URL to receive appointment event callbacks.",
    ),
)
class WebhookSubscriptionViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = WebhookSubscription.objects.all()
    serializer_class = WebhookSubscriptionSerializer
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(business=self.get_business())


@extend_schema_view(
    list=extend_schema(
        tags=["Webhooks"],
        summary="List webhook deliveries",
        description="Admin only. Delivery log for webhook subscriptions.",
    ),
)
class WebhookDeliveryViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = WebhookDelivery.objects.select_related("subscription")
    serializer_class = WebhookDeliverySerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = [IsAdminRole]
