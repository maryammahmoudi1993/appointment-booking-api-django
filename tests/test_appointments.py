from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
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


@pytest.fixture
def staff_user(db):
    s = StaffFactory()
    for day in range(5):
        WorkingHoursFactory(staff=s, weekday=day, start_time="09:00", end_time="17:00")
    return s


@pytest.fixture
def service(db):
    return ServiceFactory(duration_minutes=30, price=25.00)


@pytest.fixture
def customer_user(db):
    return CustomerFactory()


def _make_appointment_data(customer_user, staff_user, service, hour=10):
    target = _next_weekday(0)
    start = _make_aware(
        timezone.datetime.combine(
            target, timezone.datetime.min.time().replace(hour=hour, minute=0)
        )
    )
    end = start + timedelta(minutes=30)
    return {
        "customer": customer_user.id,
        "staff": staff_user.id,
        "service": service.id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
    }


@pytest.mark.django_db
class TestAppointmentList:
    def test_customer_sees_own_appointments(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        AppointmentFactory(customer=customer_user, staff=staff_user, service=service)
        other_customer = CustomerFactory()
        AppointmentFactory(customer=other_customer, staff=staff_user, service=service)
        response = api_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_staff_sees_assigned_appointments(
        self, api_client, staff_user, customer_user, service
    ):
        api_client.force_authenticate(user=staff_user)
        AppointmentFactory(customer=customer_user, staff=staff_user, service=service)
        other_staff = StaffFactory()
        AppointmentFactory(customer=customer_user, staff=other_staff, service=service)
        response = api_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_admin_sees_all_appointments(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(customer=customer_user, staff=staff_user, service=service)
        other_staff = StaffFactory()
        AppointmentFactory(customer=customer_user, staff=other_staff, service=service)
        response = api_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAppointmentCreate:
    def test_create_appointment(self, api_client, customer_user, staff_user, service):
        api_client.force_authenticate(user=customer_user)
        data = _make_appointment_data(customer_user, staff_user, service)
        response = api_client.post("/api/appointments/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_create_conflict_returns_409(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        data = _make_appointment_data(customer_user, staff_user, service)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        end = start + timedelta(minutes=30)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=end,
            status="confirmed",
        )
        response = api_client.post("/api/appointments/", data)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_unauthenticated_cannot_create(
        self, api_client, customer_user, staff_user, service
    ):
        data = _make_appointment_data(customer_user, staff_user, service)
        response = api_client.post("/api/appointments/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAppointmentCancel:
    def test_cancel_own_appointment(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appointment = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="pending",
        )
        response = api_client.post(f"/api/appointments/{appointment.id}/cancel/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "cancelled"

    def test_cancel_completed_fails(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appointment = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="completed",
        )
        response = api_client.post(f"/api/appointments/{appointment.id}/cancel/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAppointmentConfirm:
    def test_staff_can_confirm(self, api_client, staff_user, customer_user, service):
        api_client.force_authenticate(user=staff_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appointment = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="pending",
        )
        response = api_client.patch(f"/api/appointments/{appointment.id}/confirm/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "confirmed"

    def test_customer_cannot_confirm(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appointment = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="pending",
        )
        response = api_client.patch(f"/api/appointments/{appointment.id}/confirm/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAppointmentAccessControl:
    def test_customer_cannot_see_others_appointment(
        self, api_client, staff_user, service
    ):
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        api_client.force_authenticate(user=customer1)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        apt = AppointmentFactory(
            customer=customer2,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )
        response = api_client.get(f"/api/appointments/{apt.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_staff_cannot_see_other_staffs_appointment(
        self, api_client, staff_user, service
    ):
        other_staff = StaffFactory()
        customer = CustomerFactory()
        api_client.force_authenticate(user=staff_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        apt = AppointmentFactory(
            customer=customer,
            staff=other_staff,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )
        response = api_client.get(f"/api/appointments/{apt.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
