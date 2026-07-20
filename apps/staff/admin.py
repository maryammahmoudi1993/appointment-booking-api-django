from django.contrib import admin

from .models import StaffProfile, TimeOff, WorkingHours


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "weekday", "start_time", "end_time")
    list_filter = ("weekday",)


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ("staff", "start_datetime", "end_datetime", "reason")
    list_filter = ("staff",)
