from datetime import timedelta

import pytest
from django.utils import timezone

from apps.appointments.validators import validate_booking
from core.exceptions import (
    BookingConflict,
    DuringTimeOff,
    InvalidTimeRange,
    OutsideWorkingHours,
)
from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
    TimeOffFactory,
    WorkingHoursFactory,
)


@pytest.fixture
def staff(db):
    return StaffFactory()


@pytest.fixture
def customer(db):
    return CustomerFactory()


@pytest.fixture
def service(db):
    return ServiceFactory(duration_minutes=30, price=25.00)


@pytest.fixture
def setup_working_hours(staff):
    for day in range(5):
        WorkingHoursFactory(
            staff=staff, weekday=day, start_time="09:00", end_time="17:00"
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
class TestValidateBooking:
    def test_valid_booking(self, staff, service, setup_working_hours):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        validate_booking(staff.id, service.id, start, end)

    def test_overlap_identical_start(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        with pytest.raises(BookingConflict):
            validate_booking(staff.id, service.id, start, end)

    def test_overlap_partial_start_inside(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        new_start = start + timedelta(minutes=15)
        new_end = new_start + timedelta(minutes=30)
        with pytest.raises(BookingConflict):
            validate_booking(staff.id, service.id, new_start, new_end)

    def test_overlap_partial_end_inside(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        new_start = start - timedelta(minutes=15)
        new_end = new_start + timedelta(minutes=30)
        with pytest.raises(BookingConflict):
            validate_booking(staff.id, service.id, new_start, new_end)

    def test_overlap_fully_containing(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        new_start = start - timedelta(minutes=15)
        new_end = new_start + timedelta(minutes=30)
        with pytest.raises(BookingConflict):
            validate_booking(staff.id, service.id, new_start, new_end)

    def test_back_to_back_no_overlap(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        new_start = end
        new_end = new_start + timedelta(minutes=30)
        validate_booking(staff.id, service.id, new_start, new_end)

    def test_update_self_no_conflict(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        appointment = AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        validate_booking(
            staff.id, service.id, start, end, exclude_appointment_id=appointment.id
        )

    def test_outside_working_hours(self, staff, service, setup_working_hours):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=7, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        with pytest.raises(OutsideWorkingHours):
            validate_booking(staff.id, service.id, start, end)

    def test_no_working_hours(self, staff, service):
        target = _next_weekday(5)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        with pytest.raises(OutsideWorkingHours):
            validate_booking(staff.id, service.id, start, end)

    def test_during_time_off(self, staff, service, setup_working_hours):
        target = _next_weekday(0)
        to_start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        to_end = to_start + timedelta(hours=2)
        TimeOffFactory(
            staff=staff, start_datetime=to_start, end_datetime=to_end, reason="Vacation"
        )
        start = to_start + timedelta(minutes=30)
        end = start + timedelta(minutes=30)
        with pytest.raises(DuringTimeOff):
            validate_booking(staff.id, service.id, start, end)

    def test_invalid_end_before_start(self, staff, service, setup_working_hours):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start - timedelta(minutes=30)
        with pytest.raises(InvalidTimeRange):
            validate_booking(staff.id, service.id, start, end)

    def test_wrong_end_time_for_service(self, staff, service, setup_working_hours):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=60)
        with pytest.raises(InvalidTimeRange):
            validate_booking(staff.id, service.id, start, end)

    def test_cancelled_appointment_no_conflict(
        self, staff, service, customer, setup_working_hours
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="cancelled",
        )
        validate_booking(staff.id, service.id, start, end)
