from rest_framework import serializers

from .models import Notification, WebhookDelivery, WebhookSubscription


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "subject",
            "body",
            "status",
            "created_at",
            "sent_at",
        )
        read_only_fields = fields


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = (
            "id",
            "url",
            "secret",
            "is_active",
            "events",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = (
            "id",
            "subscription",
            "event_type",
            "status",
            "response_status",
            "error_message",
            "retry_count",
            "created_at",
            "completed_at",
        )
        read_only_fields = fields
