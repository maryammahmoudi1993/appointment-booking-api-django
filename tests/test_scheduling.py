from datetime import time, timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.appointments.validators import validate_booking
from apps.staff.services import get_available_slots
from core.exceptions import BookingConflict, DuringTimeOff, OutsideWorkingHours
from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
    StaffProfileFactory,
    WorkingHoursFactory,
)


def _next_weekday(weekday):
    today = timezone.now().date()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def _make_aware(dt):
    return timezone.make_aware(dt, timezone.get_current_timezone())


@pytest.mark.django_db
class TestSchedulingBuffers:
    def test_buffer_prevents_back_to_back_booking(self, db):
        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        StaffProfileFactory(user=staff, buffer_after_minutes=15)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="17:00")
        target = _next_weekday(0)
        start1 = _make_aware(
            timezone.datetime.combine(target, timezone.datetime.min.time().replace(hour=9))
        )
        end1 = start1 + timedelta(minutes=30)
        start2 = end1
        end2 = start2 + timedelta(minutes=30)

        validate_booking(staff.id, service.id, start1, end1)
        AppointmentFactory(
            customer=CustomerFactory(),
            staff=staff,
            service=service,
            start_datetime=start1,
            end_datetime=end1,
            status="confirmed",
        )
        with pytest.raises(BookingConflict):
            validate_booking(staff.id, service.id, start2, end2)

    def test_buffer_does_not_block_without_buffer(self, db):
        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        StaffProfileFactory(user=staff, buffer_after_minutes=0)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="17:00")
        target = _next_weekday(0)
        start1 = _make_aware(
            timezone.datetime.combine(target, timezone.datetime.min.time().replace(hour=9))
        )
        end1 = start1 + timedelta(minutes=30)
        start2 = end1
        end2 = start2 + timedelta(minutes=30)

        validate_booking(staff.id, service.id, start1, end1)
        AppointmentFactory(
            customer=CustomerFactory(),
            staff=staff,
            service=service,
            start_datetime=start1,
            end_datetime=end1,
            status="confirmed",
        )
        validate_booking(staff.id, service.id, start2, end2)


@pytest.mark.django_db
class TestSchedulingBreaks:
    def test_break_prevents_booking(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="17:00")
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(target, timezone.datetime.min.time().replace(hour=12))
        )
        end = start + timedelta(minutes=30)
        with pytest.raises(DuringTimeOff):
            validate_booking(staff.id, service.id, start, end)

    def test_break_not_blocking_outside_break(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="17:00")
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(target, timezone.datetime.min.time().replace(hour=10))
        )
        end = start + timedelta(minutes=30)
        validate_booking(staff.id, service.id, start, end)

    def test_break_excluded_from_available_slots(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="17:00")
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )
        target = _next_weekday(0)
        slots = get_available_slots(staff.id, target)
        lunch_slots = [
            s
            for s in slots
            if s["start"] >= time(12, 0) and s["end"] <= time(13, 0)
        ]
        assert len(lunch_slots) == 0 or all(not s["available"] for s in lunch_slots)


@pytest.mark.django_db
class TestSchedulingAvailability:
    def test_buffer_reflected_in_availability(self, db):
        staff = StaffFactory()
        StaffProfileFactory(user=staff, buffer_after_minutes=15)
        WorkingHoursFactory(staff=staff, weekday=0, start_time="09:00", end_time="10:00")
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(target, timezone.datetime.min.time().replace(hour=9))
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=CustomerFactory(),
            staff=staff,
            service=ServiceFactory(duration_minutes=30),
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        slots = get_available_slots(staff.id, target)
        slot_after = [s for s in slots if s["start"] == time(9, 30)]
        assert len(slot_after) == 1, f"Expected 1 slot at 09:30, got {[(s['start'], s['available']) for s in slots]}"
        assert slot_after[0]["available"] is False

    def test_staff_profile_timezone_in_export(self, api_client, db):
        profile = StaffProfileFactory()
        api_client.force_authenticate(user=profile.user)
        response = api_client.get(f"/api/staff/{profile.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert "timezone" in response.data
        assert "buffer_before_minutes" in response.data
        assert "buffer_after_minutes" in response.data
        assert "breaks" in response.data
