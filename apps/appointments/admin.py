from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Appointment, AppointmentAuditLog


class AppointmentAuditLogInline(admin.TabularInline):
    model = AppointmentAuditLog
    fields = ("action", "previous_status", "new_status", "changed_by", "created_at")
    readonly_fields = fields
    extra = 0
    max_num = 0
    can_delete = False
    ordering = ("-created_at",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "staff",
        "service",
        "start_datetime",
        "end_datetime",
        "status_badge",
    )
    list_filter = ("status", "staff", "service", "start_datetime")
    search_fields = (
        "customer__username",
        "customer__first_name",
        "customer__last_name",
        "staff__username",
        "service__name",
        "notes",
    )
    date_hierarchy = "start_datetime"
    readonly_fields = ("created_at", "updated_at")
    actions = ["confirm_appointments", "cancel_appointments", "complete_appointments"]
    inlines = [AppointmentAuditLogInline]

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "confirmed": "#198754",
            "cancelled": "#dc3545",
            "completed": "#0dcaf0",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.action(description="Confirm selected appointments")
    def confirm_appointments(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="confirmed")
        if updated:
            self.message_user(
                request,
                f"Successfully confirmed {updated} appointment(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No pending appointments to confirm.",
                messages.WARNING,
            )

    @admin.action(description="Cancel selected appointments")
    def cancel_appointments(self, request, queryset):
        updated = queryset.exclude(status__in=["cancelled", "completed"]).update(
            status="cancelled"
        )
        if updated:
            self.message_user(
                request,
                f"Successfully cancelled {updated} appointment(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No cancellable appointments selected.",
                messages.WARNING,
            )

    @admin.action(description="Mark selected as completed")
    def complete_appointments(self, request, queryset):
        updated = queryset.filter(status="confirmed").update(status="completed")
        if updated:
            self.message_user(
                request,
                f"Successfully marked {updated} appointment(s) as completed.",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No confirmed appointments to complete.",
                messages.WARNING,
            )
