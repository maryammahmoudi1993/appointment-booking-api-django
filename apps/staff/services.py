from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone

from apps.appointments.models import Appointment

from .models import Break, StaffProfile, TimeOff, WorkingHours

SLOT_DURATION = 30


def get_available_slots(staff_id: int, target_date, business_settings=None):
    weekday = target_date.weekday()

    staff_profile = StaffProfile.objects.filter(user_id=staff_id).first()

    staff_tz = ZoneInfo("UTC")
    if staff_profile:
        try:
            staff_tz = ZoneInfo(staff_profile.effective_timezone())
        except (KeyError, TypeError):
            pass

    buffer_before = staff_profile.buffer_before_minutes if staff_profile else 0
    buffer_after = staff_profile.buffer_after_minutes if staff_profile else 0

    working_hours = WorkingHours.objects.filter(staff_id=staff_id, weekday=weekday)
    if not working_hours.exists():
        return []

    time_offs = TimeOff.objects.filter(
        staff_id=staff_id,
        start_datetime__date__lte=target_date,
        end_datetime__date__gte=target_date,
    )

    breaks = (
        Break.objects.filter(staff_profile=staff_profile, weekday=weekday)
        if staff_profile
        else Break.objects.none()
    )

    existing = Appointment.objects.filter(
        staff_id=staff_id,
        start_datetime__date=target_date,
        status__in=["pending", "confirmed"],
    ).values_list("start_datetime", "end_datetime")

    slots = []
    for wh in working_hours:
        slot_start = timezone.make_aware(
            datetime.combine(target_date, wh.start_time), staff_tz
        )
        slot_end = timezone.make_aware(
            datetime.combine(target_date, wh.end_time), staff_tz
        )

        current = slot_start
        while current < slot_end:
            next_slot = current + timedelta(minutes=SLOT_DURATION)
            if next_slot > slot_end:
                break

            is_available = True
            appt_start = current
            appt_end = next_slot

            for bk_start, bk_end in existing:
                buffered_start = bk_start - timedelta(minutes=buffer_before)
                buffered_end = bk_end + timedelta(minutes=buffer_after)
                if appt_start < buffered_end and appt_end > buffered_start:
                    is_available = False
                    break

            if is_available:
                for to_start, to_end in time_offs.values_list(
                    "start_datetime", "end_datetime"
                ):
                    if appt_start < to_end and appt_end > to_start:
                        is_available = False
                        break

            if is_available:
                for br in breaks:
                    br_start = timezone.make_aware(
                        datetime.combine(target_date, br.start_time), staff_tz
                    )
                    br_end = timezone.make_aware(
                        datetime.combine(target_date, br.end_time), staff_tz
                    )
                    if appt_start < br_end and appt_end > br_start:
                        is_available = False
                        break

            slots.append(
                {
                    "start": current.time(),
                    "end": next_slot.time(),
                    "available": is_available,
                }
            )

            current = next_slot

    return slots
