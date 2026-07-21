from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
        ("webhook", "Webhook"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_email = models.EmailField(blank=True)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification_type} to {self.recipient_email or self.recipient} - {self.status}"


class WebhookSubscription(models.Model):
    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions",
    )
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=255, blank=True,
                               help_text="HMAC signing secret. Leave blank to auto-generate.")
    is_active = models.BooleanField(default=True)
    events = models.CharField(
        max_length=500, blank=True,
        help_text="Comma-separated event types (e.g. appointment.created,appointment.cancelled). "
                  "Leave blank to receive all events."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Webhook {self.url[:50]} for {self.business.name}"


class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]

    subscription = models.ForeignKey(
        WebhookSubscription, on_delete=models.CASCADE, related_name="deliveries"
    )
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "webhook deliveries"

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.status}"
