from django.conf import settings
from django.db import models


class Appointment(models.Model):
    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
    )
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_customer",
        limit_choices_to={"role": "customer"},
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_staff",
        limit_choices_to={"role": "staff"},
    )
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="appointments"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self) -> str:
        return (
            f"{self.customer.username} with {self.staff.username} "
            f"on {self.start_datetime:%Y-%m-%d %H:%M}"
        )


class AppointmentAuditLog(models.Model):
    ACTION_CHOICES = [
        ("status_change", "Status Change"),
        ("reschedule", "Reschedule"),
        ("created", "Created"),
        ("cancelled", "Cancelled"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
    ]

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_status = models.CharField(
        max_length=12, blank=True, choices=Appointment.STATUS_CHOICES
    )
    new_status = models.CharField(
        max_length=12, blank=True, choices=Appointment.STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointment_audit_actions",
    )
    old_start = models.DateTimeField(null=True, blank=True)
    old_end = models.DateTimeField(null=True, blank=True)
    new_start = models.DateTimeField(null=True, blank=True)
    new_end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "appointment audit logs"

    def __str__(self) -> str:
        return (
            f"{self.appointment.id} - {self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
        )
