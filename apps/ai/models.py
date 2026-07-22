import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="ai_conversations",
        null=True,
    )
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} by {self.user.username}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
        ("tool", "Tool"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(blank=True)
    tool_name = models.CharField(max_length=100, blank=True)
    tool_call_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class BookingDraft(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="booking_drafts",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_booking_drafts",
    )
    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="ai_booking_drafts",
        null=True,
    )
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="ai_drafts"
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_drafts_as_staff",
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_drafts",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Draft {self.id}: {self.service.name} on {self.start_datetime:%Y-%m-%d %H:%M}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def confirm(self):
        from apps.appointments.validators import create_appointment_atomic

        if self.is_expired():
            self.status = "expired"
            self.save(update_fields=["status"])
            return None, "This booking draft has expired. Please start a new booking."

        if self.status != "pending":
            return None, "This draft has already been processed."

        appointment = create_appointment_atomic(
            customer_id=self.user_id,
            staff_id=self.staff_id,
            service_id=self.service_id,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            notes=f"Booked via AI assistant. Draft {self.id}",
        )
        appointment._changed_by = self.user

        self.status = "confirmed"
        self.confirmed_at = timezone.now()
        self.appointment = appointment
        self.save(update_fields=["status", "confirmed_at", "appointment_id"])

        return appointment, None
