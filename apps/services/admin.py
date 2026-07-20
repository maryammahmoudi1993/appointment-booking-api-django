from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_minutes",
        "price_display",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "duration_minutes")
    search_fields = ("name", "description")
    date_hierarchy = "created_at"
    list_editable = ("is_active",)

    @admin.display(description="Price")
    def price_display(self, obj):
        return f"${obj.price:.2f}"
