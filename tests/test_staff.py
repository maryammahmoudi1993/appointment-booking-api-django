from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
    TimeOffFactory,
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
class TestStaffList:
    def test_list_staff_public(self, api_client):
        from core.business import get_default_business

        StaffProfile = __import__(
            "apps.staff.models", fromlist=["StaffProfile"]
        ).StaffProfile
        business = get_default_business()
        StaffProfile.objects.create(user=StaffFactory(), business=business)
        StaffProfile.objects.create(user=StaffFactory(), business=business)
        response = api_client.get("/api/staff/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2


@pytest.mark.django_db
class TestStaffAvailability:
    def test_availability_no_working_hours(self, api_client):
        staff = StaffFactory()
        target = _next_weekday(0)
        response = api_client.get(
            f"/api/staff/{staff.id}/availability/",
            {"date": target.strftime("%Y-%m-%d")},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["available_slots"] == []

    def test_availability_with_working_hours(self, api_client):
        staff = StaffFactory()
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="12:00"
        )
        target = _next_weekday(0)
        response = api_client.get(
            f"/api/staff/{staff.id}/availability/",
            {"date": target.strftime("%Y-%m-%d")},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["available_slots"]) > 0

    def test_availability_missing_date(self, api_client):
        staff = StaffFactory()
        response = api_client.get(f"/api/staff/{staff.id}/availability/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_availability_invalid_date_format(self, api_client):
        staff = StaffFactory()
        response = api_client.get(
            f"/api/staff/{staff.id}/availability/", {"date": "not-a-date"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_availability_excludes_bookings(self, api_client):
        staff = StaffFactory()
        customer = CustomerFactory()
        service = ServiceFactory(duration_minutes=30)
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="10:00"
        )
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=9, minute=30)
            )
        )
        AppointmentFactory(
            customer=customer,
            staff=staff,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="confirmed",
        )
        response = api_client.get(
            f"/api/staff/{staff.id}/availability/",
            {"date": target.strftime("%Y-%m-%d")},
        )
        assert response.status_code == status.HTTP_200_OK
        booked = next(
            s
            for s in response.data["available_slots"]
            if s["start"] == start.strftime("%H:%M:%S")
        )
        assert booked["available"] is False

    def test_availability_excludes_time_off(self, api_client):
        staff = StaffFactory()
        WorkingHoursFactory(
            staff=staff, weekday=0, start_time="09:00", end_time="12:00"
        )
        target = _next_weekday(0)
        to_start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10)
            )
        )
        TimeOffFactory(
            staff=staff,
            start_datetime=to_start,
            end_datetime=to_start + timedelta(hours=1),
        )
        response = api_client.get(
            f"/api/staff/{staff.id}/availability/",
            {"date": target.strftime("%Y-%m-%d")},
        )
        assert response.status_code == status.HTTP_200_OK
        blocked = next(
            s
            for s in response.data["available_slots"]
            if s["start"] == to_start.strftime("%H:%M:%S")
        )
        assert blocked["available"] is False
