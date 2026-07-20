import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.factories import AdminFactory, CustomerFactory, StaffFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return CustomerFactory()


@pytest.fixture
def staff_user(db):
    return StaffFactory()


@pytest.fixture
def admin_user(db):
    return AdminFactory()


@pytest.fixture
def auth_client(api_client, customer):
    api_client.force_authenticate(user=customer)
    return api_client


@pytest.fixture
def staff_client(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
