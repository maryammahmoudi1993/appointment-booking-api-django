from django.contrib import admin

from .models import (
    LoyaltyRedemption,
    LoyaltyReward,
    PromoCode,
    PromoRedemption,
    Review,
    SupportMessage,
)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "staff", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("customer__username", "staff__username", "comment")


@admin.register(LoyaltyReward)
class LoyaltyRewardAdmin(admin.ModelAdmin):
    list_display = ("name", "points_cost", "is_active")
    list_filter = ("is_active",)


@admin.register(LoyaltyRedemption)
class LoyaltyRedemptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "reward", "points_spent", "created_at")
    search_fields = ("customer__username", "reward__name")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "is_active", "created_at")
    list_filter = ("is_active", "discount_type")
    search_fields = ("code", "description")


@admin.register(PromoRedemption)
class PromoRedemptionAdmin(admin.ModelAdmin):
    list_display = ("promo", "customer", "discount_amount", "created_at")
    search_fields = ("promo__code", "customer__username")


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("customer", "is_read", "created_at", "replied_at")
    list_filter = ("is_read",)
    search_fields = ("customer__username", "message")
