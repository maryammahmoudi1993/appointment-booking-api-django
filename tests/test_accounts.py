import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from tests.factories import CustomerFactory

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

    def test_register_duplicate_username(self, api_client):
        CustomerFactory(username="existing")
        data = {
            "username": "existing",
            "email": "new@example.com",
            "role": "customer",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client):
        user = CustomerFactory(username="logintest")
        user.set_password("pass123")
        user.save()
        response = api_client.post(
            "/api/auth/login/", {"username": "logintest", "password": "pass123"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client):
        user = CustomerFactory(username="wrongpass")
        user.set_password("correct")
        user.save()
        response = api_client.post(
            "/api/auth/login/", {"username": "wrongpass", "password": "wrong"}
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
    def test_logout_success(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        login_resp = api_client.post(
            "/api/auth/login/",
            {"username": customer.username, "password": "testpass123"},
        )
        # Use factory-generated user with known password
        customer.set_password("testpass123")
        customer.save()
        login_resp = api_client.post(
            "/api/auth/login/",
            {"username": customer.username, "password": "testpass123"},
        )
        refresh = login_resp.data["refresh"]
        response = api_client.post("/api/auth/logout/", {"refresh": refresh})
        assert response.status_code == status.HTTP_200_OK

    def test_logout_without_token(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        response = api_client.post("/api/auth/logout/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
