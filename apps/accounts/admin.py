from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role_badge",
        "phone_number",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    date_hierarchy = "date_joined"
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "phone_number")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("role", "phone_number")}),
    )

    @admin.display(description="Role")
    def role_badge(self, obj):
        colors = {
            "customer": "#0d6efd",
            "staff": "#198754",
            "admin": "#dc3545",
        }
        color = colors.get(obj.role, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:12px;">{}</span>',
            color,
            obj.get_role_display(),
        )
