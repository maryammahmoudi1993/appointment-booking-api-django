from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "phone_number")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("role", "phone_number")}),
    )
