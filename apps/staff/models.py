from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class StaffProfile(models.Model):
    business = models.ForeignKey(
        "business.Business",
        on_delete=models.CASCADE,
        related_name="staff_profiles",
        null=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile"
    )
    bio = models.TextField(blank=True)
    services_offered = models.ManyToManyField("services.Service", blank=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"Staff: {self.user.get_full_name() or self.user.username}"


class WorkingHours(models.Model):
    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="working_hours",
        limit_choices_to={"role": "staff"},
    )
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["staff", "weekday"]
        unique_together = ["staff", "weekday"]

    def __str__(self) -> str:
        return f"{self.staff.username} - {self.get_weekday_display()}: {self.start_time}-{self.end_time}"


class TimeOff(models.Model):
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_offs",
        limit_choices_to={"role": "staff"},
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self) -> str:
        return f"{self.staff.username} off: {self.start_datetime} - {self.end_datetime}"
