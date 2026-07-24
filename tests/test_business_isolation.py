import pytest
from rest_framework import status

from apps.business.models import Business, BusinessMembership
from apps.engagement.models import LoyaltyReward, PromoCode, Review, SupportMessage
from apps.staff.models import Break, TimeOff, WorkingHours
from core.business import get_default_business, get_user_business, get_user_business_or_404
from tests.factories import (
    AdminFactory,
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffProfileFactory,
    UserFactory,
)


@pytest.fixture
def other_business(db):
    return Business.objects.create(name="Other Salon", slug="other-salon")


@pytest.mark.django_db
class TestBusinessIsolation:
    def test_other_business_service_not_visible(self, api_client, other_business):
        ServiceFactory.create_batch(2)
        ServiceFactory(business=other_business)
        response = api_client.get("/api/services/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_other_business_staff_not_visible(self, api_client, other_business):
        StaffProfileFactory.create_batch(2)
        StaffProfileFactory(business=other_business)
        response = api_client.get("/api/staff/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_cross_business_appointment_404(self, auth_client, customer, other_business):
        other_staff = StaffProfileFactory(business=other_business)
        appt = AppointmentFactory(
            customer=customer, staff=other_staff.user, business=other_business
        )
        response = auth_client.get(f"/api/appointments/{appt.id}/")
        assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN)

    def test_admin_sees_own_business_appointments_only(
        self, admin_client, admin_user, other_business
    ):
        AppointmentFactory.create_batch(3)
        AppointmentFactory(business=other_business)
        response = admin_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_staff_sees_own_business_appointments_only(
        self, staff_client, staff_user, other_business
    ):
        AppointmentFactory(staff=staff_user)
        AppointmentFactory(staff=StaffProfileFactory(business=other_business).user)
        response = staff_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_customer_member_can_access_own_business(
        self, api_client, customer, other_business
    ):
        staff_user = StaffProfileFactory().user
        AppointmentFactory(customer=customer, staff=staff_user)
        api_client.force_authenticate(user=customer)
        response = api_client.get("/api/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestBusinessMembership:
    def test_non_member_has_no_business(self, db):
        user = UserFactory()
        assert Business.objects.count() == 1
        business = Business.objects.first()
        assert not business.memberships.filter(user=user).exists()

    def test_member_has_business_access(self, db):
        user = UserFactory()
        business = Business.objects.first()
        BusinessMembership.objects.create(
            user=user, business=business, role="customer"
        )
        assert business.memberships.filter(user=user).exists()

    def test_admin_membership_allows_management(self, db):
        user = AdminFactory()
        business = Business.objects.first()
        BusinessMembership.objects.create(
            user=user, business=business, role="admin"
        )
        assert business.memberships.filter(user=user, role="admin").exists()

    def test_customer_without_membership_still_has_business(self, customer, db):
        business = Business.objects.first()
        assert not business.memberships.filter(user=customer).exists()
        assert get_default_business() == business


@pytest.mark.django_db
class TestBusinessUtilities:
    def test_get_default_business_returns_first(self, db):
        assert get_default_business() is not None
        assert get_default_business().name == "Bloom Studio"

    def test_get_user_business_without_membership_returns_none(self, db):
        user = UserFactory()
        assert get_user_business(user) is None

    def test_get_user_business_with_membership(self, db):
        user = UserFactory()
        business = get_default_business()
        BusinessMembership.objects.create(user=user, business=business, role="customer")
        assert get_user_business(user) == business

    def test_get_user_business_or_404_raises(self, db):
        user = UserFactory()
        with pytest.raises(Exception):
            get_user_business_or_404(user)


@pytest.mark.django_db
class TestEngagementBusinessIsolation:
    def test_other_business_rewards_not_visible(self, api_client, other_business):
        business = get_default_business()
        LoyaltyReward.objects.create(name="Reward A", points_cost=100, business=business)
        LoyaltyReward.objects.create(name="Reward B", points_cost=200, business=other_business)
        # Authenticate as a user in the default business
        user = CustomerFactory()
        BusinessMembership.objects.create(user=user, business=business, role="customer")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/loyalty/rewards/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_other_business_reviews_not_visible(self, api_client, other_business):
        business = get_default_business()
        staff = StaffProfileFactory().user
        cust1 = CustomerFactory()
        cust2 = CustomerFactory()
        appt1 = AppointmentFactory(customer=cust1, staff=staff, business=business, status="completed")
        appt2 = AppointmentFactory(customer=cust2, staff=staff, business=other_business, status="completed")
        Review.objects.create(appointment=appt1, customer=cust1, staff=staff, rating=5, business=business)
        Review.objects.create(appointment=appt2, customer=cust2, staff=staff, rating=4, business=other_business)
        user = CustomerFactory()
        BusinessMembership.objects.create(user=user, business=business, role="customer")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/reviews/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_other_business_promos_not_visible(self, api_client, other_business):
        business = get_default_business()
        PromoCode.objects.create(code="PROMO1", discount_type="percent", discount_value=10, business=business)
        PromoCode.objects.create(code="PROMO2", discount_type="fixed", discount_value=5, business=other_business)
        user = AdminFactory()
        BusinessMembership.objects.create(user=user, business=business, role="admin")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/promotions/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_other_business_support_messages_not_visible(self, api_client, other_business):
        business = get_default_business()
        cust1 = CustomerFactory()
        cust2 = CustomerFactory()
        SupportMessage.objects.create(customer=cust1, message="help", business=business)
        SupportMessage.objects.create(customer=cust2, message="other help", business=other_business)
        admin = AdminFactory()
        BusinessMembership.objects.create(user=admin, business=business, role="admin")
        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/support-messages/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestStaffScheduleBusinessIsolation:
    """Regression tests: WorkingHours/TimeOff/Break viewsets previously had no
    business scoping at all — any admin, from any business, could list/edit
    every business's staff schedules. See apps/staff/views.py."""

    def test_other_business_working_hours_not_visible(self, api_client, other_business):
        business = get_default_business()
        own_staff = StaffProfileFactory(business=business).user
        other_staff = StaffProfileFactory(business=other_business).user
        WorkingHours.objects.create(
            staff=own_staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        WorkingHours.objects.create(
            staff=other_staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        admin = AdminFactory()
        BusinessMembership.objects.create(user=admin, business=business, role="admin")
        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/working-hours/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_other_business_time_off_not_visible(self, api_client, other_business):
        from django.utils import timezone

        business = get_default_business()
        own_staff = StaffProfileFactory(business=business).user
        other_staff = StaffProfileFactory(business=other_business).user
        now = timezone.now()
        TimeOff.objects.create(
            staff=own_staff, start_datetime=now, end_datetime=now, reason="own"
        )
        TimeOff.objects.create(
            staff=other_staff, start_datetime=now, end_datetime=now, reason="other"
        )
        admin = AdminFactory()
        BusinessMembership.objects.create(user=admin, business=business, role="admin")
        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/time-off/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_other_business_breaks_not_visible(self, api_client, other_business):
        business = get_default_business()
        own_profile = StaffProfileFactory(business=business)
        other_profile = StaffProfileFactory(business=other_business)
        Break.objects.create(
            staff_profile=own_profile, weekday=0, start_time="12:00", end_time="13:00"
        )
        Break.objects.create(
            staff_profile=other_profile, weekday=0, start_time="12:00", end_time="13:00"
        )
        admin = AdminFactory()
        BusinessMembership.objects.create(user=admin, business=business, role="admin")
        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/breaks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_cross_business_admin_cannot_edit_other_business_working_hours(
        self, api_client, other_business
    ):
        other_staff = StaffProfileFactory(business=other_business).user
        wh = WorkingHours.objects.create(
            staff=other_staff, weekday=0, start_time="09:00", end_time="17:00"
        )
        business = get_default_business()
        admin = AdminFactory()
        BusinessMembership.objects.create(user=admin, business=business, role="admin")
        api_client.force_authenticate(user=admin)
        response = api_client.patch(
            f"/api/working-hours/{wh.id}/", {"start_time": "10:00"}, format="json"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
