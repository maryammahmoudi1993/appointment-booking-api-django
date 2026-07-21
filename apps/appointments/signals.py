from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Appointment, AppointmentAuditLog


@receiver(pre_save, sender=Appointment)
def _track_appointment_before_save(sender, instance, **kwargs):
    if not instance.pk or kwargs.get("raw", False):
        return
    try:
        orig = sender.objects.get(pk=instance.pk)
        instance._audit_prev = orig
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender=Appointment)
def _audit_appointment_changes(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return

    if created:
        AppointmentAuditLog.objects.create(
            appointment=instance,
            action="created",
            new_status=instance.status,
            new_start=instance.start_datetime,
            new_end=instance.end_datetime,
        )
        return

    prev = getattr(instance, "_audit_prev", None)
    if prev is None:
        return

    changed_by = getattr(instance, "_changed_by", None)

    if prev.status != instance.status:
        AppointmentAuditLog.objects.create(
            appointment=instance,
            action="status_change",
            previous_status=prev.status,
            new_status=instance.status,
            changed_by=changed_by,
        )

    if (
        prev.start_datetime != instance.start_datetime
        or prev.end_datetime != instance.end_datetime
    ):
        AppointmentAuditLog.objects.create(
            appointment=instance,
            action="reschedule",
            previous_status=instance.status,
            new_status=instance.status,
            changed_by=changed_by,
            old_start=prev.start_datetime,
            old_end=prev.end_datetime,
            new_start=instance.start_datetime,
            new_end=instance.end_datetime,
        )
