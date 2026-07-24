from decimal import Decimal

import pytest
from rest_framework import status

from apps.engagement.models import Review
from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
    StaffProfileFactory,
)


@pytest.fixture
def staff_user(db):
    profile = StaffProfileFactory()
    return profile.user


@pytest.fixture
def service(db):
    return ServiceFactory(duration_minutes=30, price=Decimal("50.00"))


@pytest.fixture
def customer_user(db):
    return CustomerFactory()


@pytest.fixture
def admin_client_authenticated(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.mark.django_db
class TestRevenueAnalytics:
    def test_empty_revenue_returns_zeros(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/analytics/revenue/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_revenue"] == "0.00"
        assert response.data["total_bookings"] == 0
        assert response.data["revenue_by_period"] == []

    def test_completed_appointments_count_as_revenue(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=service, status="pending"
        )
        response = api_client.get("/api/analytics/revenue/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_bookings"] == 1
        assert Decimal(response.data["total_revenue"]) == Decimal("50.00")

    def test_average_ticket_calculation(
        self, api_client, admin_user, customer_user, staff_user
    ):
        api_client.force_authenticate(user=admin_user)
        svc1 = ServiceFactory(price=Decimal("100.00"))
        svc2 = ServiceFactory(price=Decimal("200.00"))
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=svc1, status="completed"
        )
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=svc2, status="completed"
        )
        response = api_client.get("/api/analytics/revenue/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_bookings"] == 2
        assert Decimal(response.data["average_ticket"]) == Decimal("150.00")

    def test_revenue_grouped_by_month(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        response = api_client.get("/api/analytics/revenue/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["revenue_by_period"]) == 1
        assert Decimal(response.data["revenue_by_period"][0]["revenue"]) == Decimal(
            "50.00"
        )

    def test_only_admin_can_access(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/analytics/revenue/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStaffAnalytics:
    def test_staff_booking_counts(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=service, status="pending"
        )
        response = api_client.get("/api/analytics/staff/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        staff_data = response.data["results"][0]
        assert staff_data["staff_id"] == staff_user.id
        assert staff_data["total_bookings"] == 2
        assert staff_data["completed_bookings"] == 1

    def test_staff_revenue_calculation(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        response = api_client.get("/api/analytics/staff/")
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["results"][0]["total_revenue"]) == Decimal("50.00")

    def test_staff_with_reviews_shows_rating(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        apt = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        Review.objects.create(
            appointment=apt,
            customer=customer_user,
            staff=staff_user,
            rating=5,
            business=apt.business,
        )
        response = api_client.get("/api/analytics/staff/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["average_rating"] == 5.0
        assert response.data["results"][0]["review_count"] == 1

    def test_only_admin_can_access(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/analytics/staff/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_results_are_paginated(
        self, api_client, admin_user, customer_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        for _ in range(3):
            staff = StaffFactory()
            StaffProfileFactory(user=staff)
            AppointmentFactory(customer=customer_user, staff=staff, service=service)

        response = api_client.get("/api/analytics/staff/?page_size=2")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 2
        assert response.data["next"] is not None


@pytest.mark.django_db
class TestServiceAnalytics:
    def test_service_booking_counts(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="cancelled",
        )
        response = api_client.get("/api/analytics/services/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        svc_data = response.data["results"][0]
        assert svc_data["service_id"] == service.id
        assert svc_data["total_bookings"] == 2
        assert svc_data["completed_bookings"] == 1
        assert svc_data["average_duration"] == 30

    def test_service_revenue_only_from_completed(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=service, status="pending"
        )
        response = api_client.get("/api/analytics/services/")
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["results"][0]["total_revenue"]) == Decimal("50.00")

    def test_service_with_reviews_shows_rating(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        apt = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        Review.objects.create(
            appointment=apt,
            customer=customer_user,
            staff=staff_user,
            rating=4,
            business=apt.business,
        )
        response = api_client.get("/api/analytics/services/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["average_rating"] == 4.0
        assert response.data["results"][0]["review_count"] == 1

    def test_only_admin_can_access(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/analytics/services/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookingAnalytics:
    def test_empty_bookings_returns_zeros(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/analytics/bookings/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total"] == 0
        assert response.data["completion_rate"] == 0
        assert response.data["cancellation_rate"] == 0

    def test_booking_status_counts(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user, staff=staff_user, service=service, status="pending"
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="confirmed",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="cancelled",
        )
        response = api_client.get("/api/analytics/bookings/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total"] == 4
        assert response.data["pending"] == 1
        assert response.data["confirmed"] == 1
        assert response.data["completed"] == 1
        assert response.data["cancelled"] == 1

    def test_completion_rate_calculation(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        for _ in range(3):
            AppointmentFactory(
                customer=customer_user,
                staff=staff_user,
                service=service,
                status="completed",
            )
        for _ in range(2):
            AppointmentFactory(
                customer=customer_user,
                staff=staff_user,
                service=service,
                status="cancelled",
            )
        response = api_client.get("/api/analytics/bookings/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["completion_rate"] == 60.0
        assert response.data["cancellation_rate"] == 40.0

    def test_total_revenue_in_booking_stats(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            status="completed",
        )
        response = api_client.get("/api/analytics/bookings/")
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["total_revenue"]) == Decimal("50.00")

    def test_only_admin_can_access(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/analytics/bookings/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
