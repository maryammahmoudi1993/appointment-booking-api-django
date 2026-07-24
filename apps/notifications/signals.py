import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.appointments.models import Appointment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def _dispatch_notifications(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return

    if created:
        _notify_appointment_created(instance)
        return

    prev = getattr(instance, "_audit_prev", None)
    if prev is None:
        return

    if prev.status != instance.status:
        _notify_status_change(instance, prev.status, instance.status)

    if (
        prev.start_datetime != instance.start_datetime
        or prev.end_datetime != instance.end_datetime
    ):
        _notify_reschedule(instance)


def _notify_appointment_created(appointment):
    from .services import _create_notification_record

    _create_notification_record(
        business=appointment.business,
        recipient=appointment.customer,
        notification_type="email",
        subject="Appointment Booked",
        body=f"Your appointment for {appointment.service.name} "
        f"on {appointment.start_datetime:%Y-%m-%d %H:%M} has been booked.",
    )
    if appointment.business and appointment.business.email:
        _create_notification_record(
            business=appointment.business,
            recipient_email=appointment.business.email,
            notification_type="email",
            subject="New Appointment",
            body=f"New booking: {appointment.customer.get_full_name()} "
            f"for {appointment.service.name} "
            f"on {appointment.start_datetime:%Y-%m-%d %H:%M}.",
        )

    _queue_webhook(appointment, "appointment.created")


def _notify_status_change(appointment, old_status, new_status):
    from .services import _create_notification_record

    subject_map = {
        "confirmed": "Appointment Confirmed",
        "cancelled": "Appointment Cancelled",
        "completed": "Appointment Completed",
    }
    subject = subject_map.get(new_status, f"Appointment {new_status.title()}")
    _create_notification_record(
        business=appointment.business,
        recipient=appointment.customer,
        notification_type="email",
        subject=subject,
        body=f"Your appointment for {appointment.service.name} "
        f"on {appointment.start_datetime:%Y-%m-%d %H:%M} "
        f"has been {new_status}.",
    )
    _queue_webhook(appointment, f"appointment.{new_status}")


def _notify_reschedule(appointment):
    from .services import _create_notification_record

    _create_notification_record(
        business=appointment.business,
        recipient=appointment.customer,
        notification_type="email",
        subject="Appointment Rescheduled",
        body=f"Your appointment for {appointment.service.name} "
        f"has been moved to {appointment.start_datetime:%Y-%m-%d %H:%M}.",
    )
    _queue_webhook(appointment, "appointment.rescheduled")


def _queue_webhook(appointment, event_type):
    from .models import WebhookSubscription

    if not appointment.business:
        return
    subs = WebhookSubscription.objects.filter(
        business=appointment.business,
        is_active=True,
    )
    for sub in subs:
        if sub.events:
            allowed = [e.strip() for e in sub.events.split(",")]
            if event_type not in allowed:
                continue
        from .services import _create_notification_record, deliver_webhook

        payload = {
            "event": event_type,
            "appointment_id": appointment.id,
            "status": appointment.status,
            "start_datetime": appointment.start_datetime.isoformat(),
            "end_datetime": appointment.end_datetime.isoformat(),
            "customer": {
                "id": appointment.customer_id,
                "name": appointment.customer.get_full_name(),
                "email": appointment.customer.email,
            },
            "service": {
                "id": appointment.service_id,
                "name": appointment.service.name,
            },
        }
        _create_notification_record(
            business=appointment.business,
            notification_type="webhook",
            subject=event_type,
            body=str(payload),
        )
        deliver_webhook(sub, event_type, payload)
