from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    appointment = models.OneToOneField(
        "appointments.Appointment", on_delete=models.CASCADE, related_name="review"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written"
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_received"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.rating}★ by {self.customer.username} for {self.staff.username}"


class LoyaltyReward(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255, blank=True)
    points_cost = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["points_cost"]

    def __str__(self) -> str:
        return f"{self.name} ({self.points_cost} pts)"


class LoyaltyRedemption(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty_redemptions",
    )
    reward = models.ForeignKey(
        LoyaltyReward, on_delete=models.PROTECT, related_name="redemptions"
    )
    points_spent = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.customer.username} redeemed {self.reward.name}"


class PromoCode(models.Model):
    DISCOUNT_CHOICES = [("percent", "Percent off"), ("fixed", "Fixed amount off")]

    code = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_CHOICES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    max_redemptions = models.PositiveIntegerField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)


class PromoRedemption(models.Model):
    promo = models.ForeignKey(
        PromoCode, on_delete=models.CASCADE, related_name="redemptions"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="promo_redemptions",
    )
    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="promo_redemption",
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.promo.code} used by {self.customer.username}"
