from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.staff.models import StaffProfile, TimeOff, WorkingHours

from .models import Appointment


def _get_staff_buffer_minutes(staff_id: int) -> tuple:
    try:
        profile = StaffProfile.objects.get(user_id=staff_id)
        return profile.buffer_before_minutes, profile.buffer_after_minutes
    except StaffProfile.DoesNotExist:
        return 0, 0


def validate_booking(
    staff_id: int,
    service_id: int,
    start_datetime,
    end_datetime,
    exclude_appointment_id: int | None = None,
) -> None:
    from apps.services.models import Service
    from apps.staff.models import Break

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

    buffer_before, buffer_after = _get_staff_buffer_minutes(staff_id)

    weekday = start_datetime.weekday()
    working_hours = WorkingHours.objects.filter(staff_id=staff_id, weekday=weekday)
    if not working_hours.exists():
        from core.exceptions import OutsideWorkingHours

        raise OutsideWorkingHours()

    wh = working_hours.first()
    local_dt = timezone.localtime(start_datetime)
    staff_start = timezone.make_aware(
        local_dt.replace(
            hour=wh.start_time.hour,
            minute=wh.start_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        ),
        timezone.get_current_timezone(),
    )
    staff_end = timezone.make_aware(
        local_dt.replace(
            hour=wh.end_time.hour,
            minute=wh.end_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        ),
        timezone.get_current_timezone(),
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

    break_conflict = Break.objects.filter(
        staff_profile__user_id=staff_id,
        weekday=weekday,
        start_time__lt=end_datetime,
        end_time__gt=start_datetime,
    ).exists()
    if break_conflict:
        from core.exceptions import DuringTimeOff

        raise DuringTimeOff(detail="This time falls within a scheduled break.")

    buffer_query = Q(
        staff_id=staff_id,
        status__in=["pending", "confirmed"],
    )
    if buffer_before > 0 or buffer_after > 0:
        buffered_appt_start = start_datetime - timedelta(minutes=buffer_before)
        buffered_appt_end = end_datetime + timedelta(minutes=buffer_after)
        buffer_query &= Q(
            start_datetime__lt=buffered_appt_end,
            end_datetime__gte=buffered_appt_start,
        )
    else:
        buffer_query &= Q(
            start_datetime__lt=end_datetime,
            end_datetime__gt=start_datetime,
        )

    if exclude_appointment_id:
        buffer_query &= ~Q(id=exclude_appointment_id)

    with transaction.atomic():
        # select_for_update() on Appointment alone cannot prevent a race for a
        # slot with zero existing rows — there is nothing yet to lock, so two
        # concurrent requests can both pass the .exists() check below and both
        # insert. Locking a stable per-staff resource first forces concurrent
        # booking attempts for the same staff member to serialize: the second
        # transaction blocks here until the first commits (or rolls back), and
        # then re-runs the conflict check against the now-committed row.
        from apps.accounts.models import User

        User.objects.select_for_update().get(pk=staff_id)

        existing = Appointment.objects.select_for_update().filter(buffer_query)
        if existing.exists():
            from core.exceptions import BookingConflict

            raise BookingConflict()


def create_appointment_atomic(
    customer_id: int,
    staff_id: int,
    service_id: int,
    start_datetime,
    end_datetime,
    notes: str = "",
) -> Appointment:
    with transaction.atomic():
        validate_booking(staff_id, service_id, start_datetime, end_datetime)
        appointment = Appointment.objects.create(
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            notes=notes,
        )
        return appointment


def update_appointment_atomic(
    appointment_id: int,
    staff_id: int,
    service_id: int,
    start_datetime,
    end_datetime,
    changed_by=None,
) -> Appointment:
    with transaction.atomic():
        validate_booking(
            staff_id,
            service_id,
            start_datetime,
            end_datetime,
            exclude_appointment_id=appointment_id,
        )
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.start_datetime = start_datetime
        appointment.end_datetime = end_datetime
        appointment.service_id = service_id
        if changed_by:
            appointment._changed_by = changed_by
        appointment.save(
            update_fields=["start_datetime", "end_datetime", "service", "updated_at"]
        )
        return appointment


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
