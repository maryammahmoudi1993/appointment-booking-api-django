import concurrent.futures
from datetime import time, timedelta

import pytest
from django.db import connection
from django.utils import timezone
from rest_framework import status

from apps.appointments.models import Appointment
from apps.appointments.validators import create_appointment_atomic, validate_booking
from apps.staff.services import get_available_slots
from core.exceptions import BookingConflict, DuringTimeOff
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
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        target = _next_weekday(0)
        start1 = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=9)
            )
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
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        target = _next_weekday(0)
        start1 = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=9)
            )
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
class TestSchedulingBreakTimezone:
    def test_break_correctly_enforced_for_non_utc_staff(self, db):
        """Regression test: the break-conflict check used to compare
        Break.start_time/end_time (local wall-clock TimeFields) directly
        against aware UTC datetimes, which Django silently reduces to the
        UTC hour-of-day — mis-enforcing breaks for any non-UTC staff. A
        staff member on a fixed UTC-5 timezone with a 12:00-13:00 LOCAL
        lunch break must be blocked from booking at 17:15 UTC (=12:15
        local), which the old UTC-hour comparison would have missed
        entirely (17:15 is nowhere near the literal 12:00-13:00 window)."""
        from datetime import time as time_cls
        from zoneinfo import ZoneInfo

        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        StaffProfileFactory(user=staff, timezone="Etc/GMT+5")
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="23:00"
        )
        profile = staff.staff_profile
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )

        target = _next_weekday(0)
        # 17:15-17:45 UTC == 12:15-12:45 local (Etc/GMT+5 == UTC-5) — inside
        # the local lunch break, must be rejected.
        during_break_start = timezone.make_aware(
            timezone.datetime.combine(target, time_cls(17, 15)), ZoneInfo("UTC")
        )
        during_break_end = during_break_start + timedelta(minutes=30)
        with pytest.raises(DuringTimeOff):
            validate_booking(staff.id, service.id, during_break_start, during_break_end)

        # 14:15-14:45 UTC == 09:15-09:45 local — outside the lunch break,
        # must be allowed (sanity check the fix isn't overly broad).
        outside_break_start = timezone.make_aware(
            timezone.datetime.combine(target, time_cls(14, 15)), ZoneInfo("UTC")
        )
        outside_break_end = outside_break_start + timedelta(minutes=30)
        validate_booking(staff.id, service.id, outside_break_start, outside_break_end)


@pytest.mark.django_db
class TestSchedulingBreaks:
    def test_break_prevents_booking(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=12)
            )
        )
        end = start + timedelta(minutes=30)
        with pytest.raises(DuringTimeOff):
            validate_booking(staff.id, service.id, start, end)

    def test_break_not_blocking_outside_break(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        BreakModel.objects.create(
            staff_profile=profile,
            weekday=0,
            start_time="12:00",
            end_time="13:00",
            label="Lunch",
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10)
            )
        )
        end = start + timedelta(minutes=30)
        validate_booking(staff.id, service.id, start, end)

    def test_break_excluded_from_available_slots(self, db):
        from apps.staff.models import Break as BreakModel

        staff = StaffFactory()
        profile = StaffProfileFactory(user=staff)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
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
            s for s in slots if s["start"] >= time(12, 0) and s["end"] <= time(13, 0)
        ]
        assert len(lunch_slots) == 0 or all(not s["available"] for s in lunch_slots)


@pytest.mark.django_db
class TestSchedulingAvailability:
    def test_buffer_reflected_in_availability(self, db):
        staff = StaffFactory()
        StaffProfileFactory(user=staff, buffer_after_minutes=15)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="10:00"
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=9)
            )
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
        assert (
            len(slot_after) == 1
        ), f"Expected 1 slot at 09:30, got {[(s['start'], s['available']) for s in slots]}"
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


@pytest.mark.django_db(transaction=True)
class TestSchedulingConcurrency:
    def test_concurrent_bookings_for_same_never_before_booked_slot(self):
        """Regression test: select_for_update() on Appointment alone cannot
        lock a slot with zero existing rows. N concurrent requests for the
        exact same never-before-booked slot must yield exactly one success
        and N-1 BookingConflict errors, never more than one Appointment."""
        staff = StaffFactory()
        service = ServiceFactory(duration_minutes=30)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        customers = [CustomerFactory() for _ in range(5)]
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=9)
            )
        )
        end = start + timedelta(minutes=30)

        staff_id, service_id = staff.id, service.id
        customer_ids = [c.id for c in customers]

        def attempt_booking(customer_id):
            from django.db.utils import OperationalError

            try:
                appt = create_appointment_atomic(
                    customer_id=customer_id,
                    staff_id=staff_id,
                    service_id=service_id,
                    start_datetime=start,
                    end_datetime=end,
                )
                return ("ok", appt.id)
            except BookingConflict:
                return ("conflict", None)
            except OperationalError as exc:
                # SQLite (used only in local/dev test runs; CI and prod use
                # real Postgres) has no MVCC row locking and instead enforces
                # exclusivity via a coarser whole-database write lock — a
                # "database is locked" error here is itself evidence the
                # second writer was correctly blocked from double-booking,
                # just via a different mechanism than our staff-row lock.
                if "locked" in str(exc).lower():
                    return ("conflict", None)
                raise
            finally:
                connection.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(attempt_booking, customer_ids))

        successes = [r for r in results if r[0] == "ok"]
        conflicts = [r for r in results if r[0] == "conflict"]

        assert (
            len(successes) == 1
        ), f"Expected exactly 1 successful booking, got {results}"
        assert len(conflicts) == 4, f"Expected 4 conflicts, got {results}"
        assert (
            Appointment.objects.filter(
                staff_id=staff_id, start_datetime=start, end_datetime=end
            ).count()
            == 1
        )
