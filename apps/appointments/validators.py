from datetime import timedelta

from django.db import connection
from django.db.models import Q
from django.utils import timezone

from apps.staff.models import TimeOff, WorkingHours

from .models import Appointment


def validate_booking(
    staff_id: int,
    service_id: int,
    start_datetime,
    end_datetime,
    exclude_appointment_id: int | None = None,
) -> None:
    from apps.services.models import Service

    if start_datetime >= end_datetime:
        from core.exceptions import InvalidTimeRange

        raise InvalidTimeRange()

    service = Service.objects.get(id=service_id)
    expected_end = start_datetime + timedelta(minutes=service.duration_minutes)
    if end_datetime != expected_end:
        from core.exceptions import InvalidTimeRange

        raise InvalidTimeRange(
            detail=f"End time must be {expected_end.strftime('%H:%M')} for a {service.duration_minutes}-minute service."
        )

    weekday = start_datetime.weekday()
    working_hours = WorkingHours.objects.filter(staff_id=staff_id, weekday=weekday)
    if not working_hours.exists():
        from core.exceptions import OutsideWorkingHours

        raise OutsideWorkingHours()

    wh = working_hours.first()
    staff_start = timezone.make_aware(
        timezone.localtime(start_datetime).replace(
            hour=wh.start_time.hour,
            minute=wh.start_time.minute,
            second=0,
            microsecond=0,
        )
    )
    staff_end = timezone.make_aware(
        timezone.localtime(start_datetime).replace(
            hour=wh.end_time.hour,
            minute=wh.end_time.minute,
            second=0,
            microsecond=0,
        )
    )
    if start_datetime < staff_start or end_datetime > staff_end:
        from core.exceptions import OutsideWorkingHours

        raise OutsideWorkingHours()

    time_off_conflict = TimeOff.objects.filter(
        staff_id=staff_id,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    ).exists()
    if time_off_conflict:
        from core.exceptions import DuringTimeOff

        raise DuringTimeOff()

    overlap_query = Q(
        staff_id=staff_id,
        status__in=["pending", "confirmed"],
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    )
    if exclude_appointment_id:
        overlap_query &= ~Q(id=exclude_appointment_id)

    if Appointment.objects.filter(overlap_query).exists():
        from core.exceptions import BookingConflict

        raise BookingConflict()


def get_available_slots_for_date(staff_id: int, target_date):
    from datetime import datetime

    weekday = target_date.weekday()
    working_hours = WorkingHours.objects.filter(staff_id=staff_id, weekday=weekday)
    if not working_hours.exists():
        return []

    time_offs = TimeOff.objects.filter(
        staff_id=staff_id,
        start_datetime__date__lte=target_date,
        end_datetime__date__gte=target_date,
    )

    existing_bookings = Appointment.objects.filter(
        staff_id=staff_id,
        start_datetime__date=target_date,
        status__in=["pending", "confirmed"],
    ).values_list("start_datetime", "end_datetime")

    slots = []
    for wh in working_hours:
        slot_start = timezone.make_aware(datetime.combine(target_date, wh.start_time))
        slot_end = timezone.make_aware(datetime.combine(target_date, wh.end_time))

        current = slot_start
        while current < slot_end:
            next_slot = current + timedelta(minutes=30)
            if next_slot > slot_end:
                next_slot = slot_end

            is_available = True

            for to_start, to_end in time_offs.values_list(
                "start_datetime", "end_datetime"
            ):
                if current < to_end and next_slot > to_start:
                    is_available = False
                    break

            if is_available:
                for bk_start, bk_end in existing_bookings:
                    if current < bk_end and next_slot > bk_start:
                        is_available = False
                        break

            if is_available:
                slots.append(
                    {
                        "start": current.time().isoformat(),
                        "end": next_slot.time().isoformat(),
                    }
                )

            current = next_slot

    return slots
