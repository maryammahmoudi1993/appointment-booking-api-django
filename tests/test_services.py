import pytest
from rest_framework import status

from tests.factories import ServiceFactory


@pytest.mark.django_db
class TestServiceList:
    def test_list_services_public(self, api_client):
        ServiceFactory.create_batch(3)
        response = api_client.get("/api/services/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_list_services_unauthenticated(self, api_client):
        ServiceFactory.create_batch(2)
        response = api_client.get("/api/services/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestServiceCreate:
    def test_admin_can_create_service(self, admin_client):
        data = {
            "name": "New Service",
            "description": "A new service",
            "duration_minutes": 45,
            "price": "50.00",
        }
        response = admin_client.post("/api/services/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Service"

    def test_created_service_is_visible_in_listing(self, admin_client):
        """Regression test: services created via POST previously got
        business=None and silently never appeared in any listing again."""
        from apps.services.models import Service

        data = {
            "name": "Visible Service",
            "description": "Must show up after creation",
            "duration_minutes": 30,
            "price": "40.00",
        }
        create_response = admin_client.post("/api/services/", data, format="json")
        assert create_response.status_code == status.HTTP_201_CREATED

        service = Service.objects.get(id=create_response.data["id"])
        assert service.business is not None

        list_response = admin_client.get("/api/services/")
        names = [s["name"] for s in list_response.data["results"]]
        assert "Visible Service" in names

    def test_customer_cannot_create_service(self, auth_client):
        data = {
            "name": "New Service",
            "duration_minutes": 45,
            "price": "50.00",
        }
        response = auth_client.post("/api/services/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_service(self, api_client):
        data = {
            "name": "New Service",
            "duration_minutes": 45,
            "price": "50.00",
        }
        response = api_client.post("/api/services/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestServiceUpdate:
    def test_admin_can_update_service(self, admin_client):
        service = ServiceFactory(name="Old Name")
        response = admin_client.patch(
            f"/api/services/{service.id}/", {"name": "New Name"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "New Name"

    def test_customer_cannot_update_service(self, auth_client):
        service = ServiceFactory()
        response = auth_client.patch(f"/api/services/{service.id}/", {"name": "Hacked"})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestServiceDelete:
    def test_admin_can_delete_service(self, admin_client):
        service = ServiceFactory()
        response = admin_client.delete(f"/api/services/{service.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_customer_cannot_delete_service(self, auth_client):
        service = ServiceFactory()
        response = auth_client.delete(f"/api/services/{service.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
