from django.contrib import admin

from .models import Business, BusinessMembership, BusinessSettings


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "business_type", "is_active"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "business",
        "slot_interval_minutes",
        "loyalty_enabled",
        "ai_enabled",
    ]


@admin.register(BusinessMembership)
class BusinessMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "business", "role"]
    list_filter = ["business", "role"]
