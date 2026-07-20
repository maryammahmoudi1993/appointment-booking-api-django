from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer", "staff", "service", "start_datetime", "status")
    list_filter = ("status",)
    search_fields = ("customer__username", "staff__username", "service__name")
