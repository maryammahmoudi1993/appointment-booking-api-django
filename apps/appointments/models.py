from django.conf import settings
from django.db import models


class Appointment(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self) -> str:
        return (
            f"{self.customer.username} with {self.staff.username} "
            f"on {self.start_datetime:%Y-%m-%d %H:%M}"
        )
