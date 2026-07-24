from django.conf import settings
from django.db import models


class Business(models.Model):
    BUSINESS_TYPES = [
        ("beauty_salon", "Beauty Salon"),
        ("massage", "Massage Center"),
        ("clinic", "Clinic"),
        ("consultant", "Consultant"),
        ("coach", "Coach"),
        ("repair_shop", "Repair Shop"),
        ("wellness", "Wellness Center"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    business_type = models.CharField(
        max_length=20, choices=BUSINESS_TYPES, default="other"
    )
    timezone = models.CharField(max_length=50, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    logo = models.URLField(blank=True, max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "businesses"

    def __str__(self) -> str:
        return self.name


class BusinessSettings(models.Model):
    business = models.OneToOneField(
        Business, on_delete=models.CASCADE, related_name="settings"
    )
    slot_interval_minutes = models.PositiveIntegerField(default=30)
    minimum_booking_notice_minutes = models.PositiveIntegerField(default=60)
    maximum_advance_booking_days = models.PositiveIntegerField(default=60)
    cancellation_window_hours = models.PositiveIntegerField(default=24)
    default_buffer_before_minutes = models.PositiveIntegerField(default=0)
    default_buffer_after_minutes = models.PositiveIntegerField(default=0)
    require_manual_confirmation = models.BooleanField(default=True)
    loyalty_enabled = models.BooleanField(default=False)
    ai_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "business settings"

    def __str__(self) -> str:
        return f"Settings for {self.business.name}"


class BusinessMembership(models.Model):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_memberships",
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "business"]
        ordering = ["-created_at"]
        verbose_name_plural = "business memberships"

    def __str__(self) -> str:
        return (
            f"{self.user.username} @ {self.business.name} ({self.get_role_display()})"
        )
