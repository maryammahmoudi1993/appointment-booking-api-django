from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from apps.engagement.models import LoyaltyReward, PromoCode, Review
from core.business import get_default_business
from tests.factories import (
    AdminFactory,
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
)


def _completed_appointment(customer, staff, service, points=50):
    appt = AppointmentFactory(
        customer=customer, staff=staff, service=service, status="completed"
    )
    appt.points_earned = points
    appt.save(update_fields=["points_earned"])
    return appt


@pytest.mark.django_db
class TestAppointmentComplete:
    def test_staff_completes_confirmed_appointment_awards_points(
        self, staff_client, staff_user, customer, service
    ):
        service.price = Decimal("42.00")
        service.save()
        appt = AppointmentFactory(
            customer=customer, staff=staff_user, service=service, status="confirmed"
        )
        response = staff_client.patch(f"/api/appointments/{appt.id}/complete/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "completed"
        assert response.data["points_earned"] == 42

    def test_cannot_complete_pending_appointment(
        self, staff_client, staff_user, customer, service
    ):
        appt = AppointmentFactory(
            customer=customer, staff=staff_user, service=service, status="pending"
        )
        response = staff_client.patch(f"/api/appointments/{appt.id}/complete/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_customer_cannot_complete_appointment(
        self, auth_client, customer, staff_user, service
    ):
        appt = AppointmentFactory(
            customer=customer, staff=staff_user, service=service, status="confirmed"
        )
        response = auth_client.patch(f"/api/appointments/{appt.id}/complete/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReviews:
    def test_customer_can_review_completed_appointment(
        self, auth_client, customer, staff_user, service
    ):
        appt = _completed_appointment(customer, staff_user, service)
        response = auth_client.post(
            "/api/reviews/", {"appointment": appt.id, "rating": 5, "comment": "Great!"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(appointment=appt).exists()

    def test_cannot_review_pending_appointment(
        self, auth_client, customer, staff_user, service
    ):
        appt = AppointmentFactory(
            customer=customer, staff=staff_user, service=service, status="pending"
        )
        response = auth_client.post(
            "/api/reviews/", {"appointment": appt.id, "rating": 4}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_review_twice(self, auth_client, customer, staff_user, service):
        appt = _completed_appointment(customer, staff_user, service)
        Review.objects.create(
            appointment=appt, customer=customer, staff=staff_user, rating=5
        )
        response = auth_client.post(
            "/api/reviews/", {"appointment": appt.id, "rating": 3}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_review_someone_elses_appointment(
        self, auth_client, staff_user, service
    ):
        other_customer = AppointmentFactory(staff=staff_user, service=service).customer
        appt = _completed_appointment(other_customer, staff_user, service)
        response = auth_client.post(
            "/api/reviews/", {"appointment": appt.id, "rating": 5}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reviews_list_is_public(self, api_client):
        response = api_client.get("/api/reviews/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLoyalty:
    def test_balance_reflects_completed_visits(
        self, auth_client, customer, staff_user, service
    ):
        _completed_appointment(customer, staff_user, service, points=30)
        _completed_appointment(customer, staff_user, service, points=20)
        response = auth_client.get("/api/loyalty/summary/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["balance"] == 50
        assert len(response.data["history"]) == 2

    def test_redeem_reward_deducts_points(
        self, auth_client, customer, staff_user, service
    ):
        _completed_appointment(customer, staff_user, service, points=100)
        reward = LoyaltyReward.objects.create(
            name="10% off", points_cost=50, business=get_default_business()
        )
        response = auth_client.post(f"/api/loyalty/rewards/{reward.id}/redeem/")
        assert response.status_code == status.HTTP_201_CREATED

        summary = auth_client.get("/api/loyalty/summary/")
        assert summary.data["balance"] == 50

    def test_redeem_fails_with_insufficient_points(
        self, auth_client, customer, staff_user, service
    ):
        reward = LoyaltyReward.objects.create(
            name="Free massage", points_cost=500, business=get_default_business()
        )
        response = auth_client.post(f"/api/loyalty/rewards/{reward.id}/redeem/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_only_admin_can_create_reward(self, auth_client):
        response = auth_client.post(
            "/api/loyalty/rewards/", {"name": "Free cut", "points_cost": 10}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = auth_client.get("/api/loyalty/rewards/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPromotions:
    def test_admin_can_create_promo_code(self, admin_client):
        response = admin_client.post(
            "/api/promotions/",
            {
                "code": "welcome15",
                "discount_type": "percent",
                "discount_value": "15.00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "WELCOME15"

    def test_non_admin_cannot_list_promotions(self, auth_client):
        response = auth_client.get("/api/promotions/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_validate_active_code(self, auth_client):
        PromoCode.objects.create(
            code="SAVE10", discount_type="fixed", discount_value=Decimal("10.00")
        )
        response = auth_client.post("/api/promotions/validate/", {"code": "save10"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "SAVE10"

    def test_validate_inactive_code_fails(self, auth_client):
        PromoCode.objects.create(
            code="OLD5",
            discount_type="fixed",
            discount_value=Decimal("5.00"),
            is_active=False,
        )
        response = auth_client.post("/api/promotions/validate/", {"code": "OLD5"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_booking_with_valid_promo_creates_redemption(
        self, auth_client, customer, staff_user, service
    ):
        from tests.factories import WorkingHoursFactory

        service.price = Decimal("100.00")
        service.save()
        PromoCode.objects.create(
            code="TENOFF", discount_type="fixed", discount_value=Decimal("10.00")
        )
        WorkingHoursFactory(
            staff=staff_user, weekday=0, start_time="09:00", end_time="17:00"
        )

        target = timezone.now().date()
        days_ahead = (0 - target.weekday()) % 7 or 7
        target = target + timedelta(days=days_ahead)
        start = timezone.make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=10)
            )
        )
        response = auth_client.post(
            "/api/appointments/",
            {
                "customer": customer.id,
                "staff": staff_user.id,
                "service": service.id,
                "start_datetime": start.isoformat(),
                "end_datetime": (start + timedelta(minutes=30)).isoformat(),
                "promo_code": "tenoff",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["discount_amount"] == "10.00"

    def test_booking_with_invalid_promo_fails(
        self, auth_client, customer, staff_user, service
    ):
        from tests.factories import WorkingHoursFactory

        WorkingHoursFactory(
            staff=staff_user, weekday=0, start_time="09:00", end_time="17:00"
        )
        target = timezone.now().date()
        days_ahead = (0 - target.weekday()) % 7 or 7
        target = target + timedelta(days=days_ahead)
        start = timezone.make_aware(
            timezone.datetime.combine(
                target, timezone.datetime.min.time().replace(hour=11)
            )
        )
        response = auth_client.post(
            "/api/appointments/",
            {
                "customer": customer.id,
                "staff": staff_user.id,
                "service": service.id,
                "start_datetime": start.isoformat(),
                "end_datetime": (start + timedelta(minutes=30)).isoformat(),
                "promo_code": "DOESNOTEXIST",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        from apps.appointments.models import Appointment

        assert not Appointment.objects.filter(
            staff=staff_user, start_datetime=start
        ).exists()

    def test_promo_scoped_to_service_applies(self, auth_client, service):
        promo = PromoCode.objects.create(
            code="HAIRONLY", discount_type="percent", discount_value=Decimal("10.00")
        )
        promo.services.add(service)
        response = auth_client.post(
            "/api/promotions/validate/", {"code": "HAIRONLY", "service": service.id}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_promo_scoped_to_service_rejects_other_service(self, auth_client, service):
        other_service = ServiceFactory()
        promo = PromoCode.objects.create(
            code="HAIRONLY2", discount_type="percent", discount_value=Decimal("10.00")
        )
        promo.services.add(service)
        response = auth_client.post(
            "/api/promotions/validate/",
            {"code": "HAIRONLY2", "service": other_service.id},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_promo_with_no_services_applies_to_any(self, auth_client, service):
        PromoCode.objects.create(
            code="ANYSERVICE", discount_type="percent", discount_value=Decimal("10.00")
        )
        response = auth_client.post(
            "/api/promotions/validate/", {"code": "ANYSERVICE", "service": service.id}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSupportMessages:
    def test_customer_can_send_message(self, auth_client):
        response = auth_client.post(
            "/api/support-messages/", {"message": "Can I reschedule tomorrow's visit?"}
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_customer_only_sees_own_messages(self, auth_client, customer):
        from apps.engagement.models import SupportMessage
        from tests.factories import CustomerFactory

        business = get_default_business()
        SupportMessage.objects.create(
            customer=customer, message="mine", business=business
        )
        SupportMessage.objects.create(
            customer=CustomerFactory(), message="not mine", business=business
        )
        response = auth_client.get("/api/support-messages/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_admin_sees_all_messages_inbox(self, admin_client, customer):
        from apps.engagement.models import SupportMessage

        SupportMessage.objects.create(
            customer=customer, message="hello", business=get_default_business()
        )
        response = admin_client.get("/api/support-messages/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_admin_can_reply(self, admin_client, customer):
        from apps.engagement.models import SupportMessage

        msg = SupportMessage.objects.create(
            customer=customer, message="hello", business=get_default_business()
        )
        response = admin_client.post(
            f"/api/support-messages/{msg.id}/reply/", {"reply": "We'll call you back."}
        )
        assert response.status_code == status.HTTP_200_OK
        msg.refresh_from_db()
        assert msg.admin_reply == "We'll call you back."
        assert msg.is_read is True

    def test_customer_cannot_reply(self, auth_client, customer):
        from apps.engagement.models import SupportMessage

        msg = SupportMessage.objects.create(
            customer=customer, message="hello", business=get_default_business()
        )
        response = auth_client.post(
            f"/api/support-messages/{msg.id}/reply/", {"reply": "nope"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPromoEdgeCases:
    def test_expired_promo_fails(self, auth_client):
        business = get_default_business()
        PromoCode.objects.create(
            code="EXPIRED",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            ends_at=timezone.now() - timedelta(days=1),
            business=business,
        )
        response = auth_client.post("/api/promotions/validate/", {"code": "EXPIRED"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_future_promo_fails(self, auth_client):
        business = get_default_business()
        PromoCode.objects.create(
            code="FUTURE",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            starts_at=timezone.now() + timedelta(days=7),
            business=business,
        )
        response = auth_client.post("/api/promotions/validate/", {"code": "FUTURE"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_max_redemptions_exceeded_fails(self, auth_client):
        business = get_default_business()
        promo = PromoCode.objects.create(
            code="LIMITED",
            discount_type="fixed",
            discount_value=Decimal("5.00"),
            max_redemptions=1,
            business=business,
        )
        from apps.engagement.models import PromoRedemption

        PromoRedemption.objects.create(
            promo=promo,
            customer=CustomerFactory(),
            discount_amount=5,
            business=business,
        )
        response = auth_client.post("/api/promotions/validate/", {"code": "LIMITED"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_inactive_reward_redemption_fails(
        self, auth_client, customer, staff_user, service
    ):
        _completed_appointment(customer, staff_user, service, points=100)
        reward = LoyaltyReward.objects.create(
            name="Inactive",
            points_cost=50,
            is_active=False,
            business=get_default_business(),
        )
        response = auth_client.post(f"/api/loyalty/rewards/{reward.id}/redeem/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_promo_redemption_endpoint_admin_only(self, api_client):
        customer = CustomerFactory()
        admin = AdminFactory()
        api_client.force_authenticate(user=customer)
        response = api_client.get("/api/promo-redemptions/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/promo-redemptions/")
        assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def service(db):
    return ServiceFactory()
