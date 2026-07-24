import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory

from core.permissions import IsAdminRole, IsOwnerOrStaffOrAdmin, IsStaffRole
from tests.factories import AdminFactory, CustomerFactory, StaffFactory

User = get_user_model()


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "testpass123",
            "first_name": "New",
            "last_name": "User",
            "role": "customer",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert response.data["user"]["username"] == "newuser"
        assert "password" not in response.data["user"]

        user = User.objects.get(username="newuser")
        assert user.check_password("testpass123")

    def test_register_duplicate_username(self, api_client):
        CustomerFactory(username="existing")
        data = {
            "username": "existing",
            "email": "new@example.com",
            "password": "pass123",
            "role": "customer",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_then_login(self, api_client):
        data = {
            "username": "logincheck",
            "email": "login@example.com",
            "password": "mypassword",
            "role": "customer",
        }
        api_client.post("/api/auth/register/", data)
        response = api_client.post(
            "/api/auth/login/",
            {"username": "logincheck", "password": "mypassword"},
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client):
        user = CustomerFactory(username="logintest")
        user.set_password("pass123")
        user.save()
        response = api_client.post(
            "/api/auth/login/",
            {"username": "logintest", "password": "pass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client):
        user = CustomerFactory(username="wrongpass")
        user.set_password("correct")
        user.save()
        response = api_client.post(
            "/api/auth/login/",
            {"username": "wrongpass", "password": "wrong"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMe:
    def test_get_me_authenticated(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == customer.username

    def test_get_me_unauthenticated(self, api_client):
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_me(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        response = api_client.patch("/api/auth/me/", {"phone_number": "+1234567890"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone_number"] == "+1234567890"


@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, api_client):
        user = CustomerFactory()
        user.set_password("testpass123")
        user.save()
        api_client.force_authenticate(user=user)
        login_resp = api_client.post(
            "/api/auth/login/",
            {"username": user.username, "password": "testpass123"},
        )
        refresh = login_resp.data["refresh"]
        response = api_client.post("/api/auth/logout/", {"refresh": refresh})
        assert response.status_code == status.HTTP_200_OK

    def test_logout_without_token(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        response = api_client.post("/api/auth/logout/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPermissions:
    def test_is_staff_role_allows_staff(self):
        user = StaffFactory()
        request = APIRequestFactory().get("/")
        request.user = user
        assert IsStaffRole().has_permission(request, None)

    def test_is_staff_role_rejects_customer(self):
        user = CustomerFactory()
        request = APIRequestFactory().get("/")
        request.user = user
        assert not IsStaffRole().has_permission(request, None)

    def test_is_staff_role_rejects_anon(self):
        request = APIRequestFactory().get("/")
        request.user = None
        assert not IsStaffRole().has_permission(request, None)

    def test_is_admin_role_allows_admin(self):
        user = AdminFactory()
        request = APIRequestFactory().get("/")
        request.user = user
        assert IsAdminRole().has_permission(request, None)

    def test_is_owner_or_staff_admin_allows_admin(self, admin_user):
        request = APIRequestFactory().get("/")
        request.user = admin_user
        assert IsOwnerOrStaffOrAdmin().has_object_permission(request, None, None)

    def test_is_owner_or_staff_rejects_other_customer(self, customer, staff_user, db):
        from tests.factories import AppointmentFactory

        appt = AppointmentFactory(customer=customer, staff=staff_user)
        other = CustomerFactory()
        request = APIRequestFactory().get("/")
        request.user = other
        assert not IsOwnerOrStaffOrAdmin().has_object_permission(request, None, appt)
