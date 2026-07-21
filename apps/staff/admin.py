from django.contrib import admin

from .models import Break, StaffProfile, TimeOff, WorkingHours


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_role", "services_count", "bio_preview")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "bio",
    )

    @admin.display(description="Role")
    def user_role(self, obj):
        return obj.user.get_role_display()

    @admin.display(description="Services")
    def services_count(self, obj):
        return obj.services_offered.count()

    @admin.display(description="Bio")
    def bio_preview(self, obj):
        if len(obj.bio) > 80:
            return obj.bio[:80] + "..."
        return obj.bio


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "weekday_display", "start_time", "end_time")
    list_filter = ("weekday", "staff")
    search_fields = ("staff__username",)

    @admin.display(description="Day")
    def weekday_display(self, obj):
        return obj.get_weekday_display()


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ("staff", "start_datetime", "end_datetime", "reason", "duration")
    list_filter = ("staff", "start_datetime")
    search_fields = ("staff__username", "reason")
    date_hierarchy = "start_datetime"

    @admin.display(description="Duration")
    def duration(self, obj):
        delta = obj.end_datetime - obj.start_datetime
        hours = delta.total_seconds() / 3600
        if hours == int(hours):
            return f"{int(hours)}h"
        return f"{hours:.1f}h"


@admin.register(Break)
class BreakAdmin(admin.ModelAdmin):
    list_display = ("staff_profile", "weekday_display", "start_time", "end_time", "label")
    list_filter = ("weekday", "staff_profile")
    search_fields = ("staff_profile__user__username", "label")

    @admin.display(description="Day")
    def weekday_display(self, obj):
        return obj.get_weekday_display()
