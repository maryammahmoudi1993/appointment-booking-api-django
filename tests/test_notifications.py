from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
import requests
from django.utils import timezone
from rest_framework import status

from apps.notifications.models import Notification, WebhookDelivery, WebhookSubscription
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
class TestNotificationCreatedOnAppointment:
    def test_created_when_appointment_booked(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        data = _make_appointment_data(customer_user, staff_user, service)
        response = api_client.post("/api/appointments/", data)
        assert response.status_code == status.HTTP_201_CREATED
        notifs = Notification.objects.filter(recipient=customer_user)
        assert notifs.count() >= 1
        assert any("booked" in n.subject.lower() for n in notifs)

    def test_created_when_appointment_confirmed(
        self, api_client, staff_user, customer_user, service
    ):
        api_client.force_authenticate(user=staff_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appt = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="pending",
        )
        api_client.patch(f"/api/appointments/{appt.id}/confirm/")
        notifs = Notification.objects.filter(recipient=customer_user)
        assert any("confirmed" in n.subject.lower() for n in notifs)

    def test_created_when_appointment_cancelled(
        self, api_client, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=customer_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appt = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="pending",
        )
        api_client.post(f"/api/appointments/{appt.id}/cancel/")
        notifs = Notification.objects.filter(recipient=customer_user)
        assert any("cancelled" in n.subject.lower() for n in notifs)

    def test_created_when_appointment_completed(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        api_client.force_authenticate(user=admin_user)
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        appt = AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
            status="confirmed",
        )
        api_client.patch(f"/api/appointments/{appt.id}/complete/")
        notifs = Notification.objects.filter(recipient=customer_user)
        assert any("completed" in n.subject.lower() for n in notifs)


@pytest.mark.django_db
class TestWebhookSubscriptionAPI:
    def test_admin_can_create_subscription(self, admin_client):
        data = {
            "url": "https://example.com/webhook",
            "events": "appointment.created,appointment.cancelled",
        }
        response = admin_client.post("/api/webhook-subscriptions/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["url"] == data["url"]
        assert response.data["events"] == data["events"]

    def test_non_admin_cannot_create_subscription(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        data = {"url": "https://example.com/webhook"}
        response = api_client.post("/api/webhook-subscriptions/", data)
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_admin_can_list_subscriptions(self, admin_client):
        response = admin_client.get("/api/webhook-subscriptions/")
        assert response.status_code == status.HTTP_200_OK

    def test_non_admin_cannot_list_subscriptions(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/webhook-subscriptions/")
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        )


@pytest.mark.django_db
class TestNotificationAPI:
    def test_admin_can_list_notifications(
        self, admin_client, customer_user, staff_user, service
    ):
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )
        response = admin_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_non_admin_cannot_list_notifications(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/notifications/")
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        )


@pytest.mark.django_db
class TestWebhookDelivery:
    @patch("requests.post")
    def test_webhook_delivered_on_appointment_created(
        self, mock_post, db, customer_user, staff_user, service
    ):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"
        mock_post.return_value = mock_resp

        from apps.business.models import Business

        business = Business.objects.first()
        sub = WebhookSubscription.objects.create(
            business=business,
            url="https://example.com/webhook",
            secret="test-secret",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
        )
        deliveries = WebhookDelivery.objects.filter(subscription=sub)
        assert deliveries.count() >= 1
        created = deliveries.filter(event_type="appointment.created").first()
        assert created is not None

    @patch("requests.post")
    def test_webhook_delivery_success(
        self, mock_post, db, customer_user, staff_user, service
    ):
        from apps.business.models import Business

        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"
        mock_post.return_value = mock_resp

        business = Business.objects.first()
        sub = WebhookSubscription.objects.create(
            business=business,
            url="https://example.com/webhook",
            secret="test-secret",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
        )
        deliveries = WebhookDelivery.objects.filter(subscription=sub)
        successful = deliveries.filter(
            status="success", event_type="appointment.created"
        ).first()
        assert successful is not None
        assert successful.response_status == 200
        assert successful.completed_at is not None

    @patch("requests.post")
    def test_webhook_delivery_failure(
        self, mock_post, db, customer_user, staff_user, service
    ):
        from apps.business.models import Business

        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.text = "Server Error"
        mock_post.return_value = mock_resp

        business = Business.objects.first()
        sub = WebhookSubscription.objects.create(
            business=business,
            url="https://example.com/webhook",
            secret="test-secret",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
        )
        deliveries = WebhookDelivery.objects.filter(subscription=sub)
        failed = deliveries.filter(
            status="failed", event_type="appointment.created"
        ).first()
        assert failed is not None
        assert failed.response_status == 500
        assert "Server Error" in failed.response_body

    @patch("requests.post")
    def test_webhook_delivery_exception(
        self, mock_post, db, customer_user, staff_user, service
    ):
        from apps.business.models import Business

        mock_post.side_effect = requests.RequestException("Connection refused")

        business = Business.objects.first()
        sub = WebhookSubscription.objects.create(
            business=business,
            url="https://example.com/webhook",
            secret="test-secret",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
        )
        deliveries = WebhookDelivery.objects.filter(subscription=sub)
        failed = deliveries.filter(
            status="failed", event_type="appointment.created"
        ).first()
        assert failed is not None
        assert "Connection refused" in failed.error_message

    def test_webhook_event_filtering(self, db, customer_user, staff_user, service):
        from apps.business.models import Business

        business = Business.objects.first()
        sub = WebhookSubscription.objects.create(
            business=business,
            url="https://example.com/webhook",
            events="appointment.cancelled",
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
        )
        deliveries = WebhookDelivery.objects.filter(subscription=sub)
        assert deliveries.count() == 0


@pytest.mark.django_db
class TestNotificationBusinessIsolation:
    def test_notification_scoped_to_business(
        self, api_client, admin_user, customer_user, staff_user, service
    ):
        from apps.business.models import Business

        other_biz = Business.objects.create(name="Other Co", slug="other-co")
        target = _next_weekday(0)
        start = _make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10, minute=0)
            )
        )
        AppointmentFactory(
            customer=customer_user,
            staff=staff_user,
            service=service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )
        Notification.objects.create(business=other_biz, notification_type="email")
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK
        for n in response.data["results"]:
            if n.get("business"):
                assert n["business"] != other_biz.id


@pytest.mark.django_db
class TestWebhookBusinessIsolation:
    def test_webhook_subscription_scoped_to_business(self, api_client, admin_user):
        from apps.business.models import Business

        business = Business.objects.first()
        other_biz = Business.objects.create(name="Other Co", slug="other-co")
        WebhookSubscription.objects.create(
            business=other_biz, url="https://other.com/hook"
        )
        WebhookSubscription.objects.create(
            business=business, url="https://mine.com/hook"
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/webhook-subscriptions/")
        assert response.status_code == status.HTTP_200_OK
        urls = [s["url"] for s in response.data["results"]]
        assert "https://mine.com/hook" in urls
        assert "https://other.com/hook" not in urls
