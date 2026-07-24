from django.contrib import admin

from .models import Notification, WebhookDelivery, WebhookSubscription


class WebhookDeliveryInline(admin.TabularInline):
    model = WebhookDelivery
    fields = ("event_type", "status", "response_status", "retry_count", "created_at")
    readonly_fields = fields
    extra = 0
    max_num = 0
    can_delete = False
    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "notification_type",
        "recipient",
        "recipient_email",
        "subject",
        "status",
        "business",
        "created_at",
    )
    list_filter = ("notification_type", "status", "business")
    search_fields = ("recipient__email", "recipient__username", "subject", "body")
    readonly_fields = ("created_at", "sent_at")
    date_hierarchy = "created_at"


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "business", "is_active", "events", "created_at")
    list_filter = ("is_active", "business")
    search_fields = ("url",)
    inlines = [WebhookDeliveryInline]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscription",
        "event_type",
        "status",
        "response_status",
        "retry_count",
        "created_at",
    )
    list_filter = ("status", "event_type")
    search_fields = ("event_type",)
    readonly_fields = ("created_at", "completed_at")
