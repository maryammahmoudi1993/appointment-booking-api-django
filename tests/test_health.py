from unittest.mock import patch

from django.db import connection
from django.db.utils import OperationalError
from rest_framework import status


class TestHealthLive:
    def test_live_returns_200(self, api_client):
        resp = api_client.get("/api/health/live/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == {"status": "alive"}


class TestHealthReady:
    def test_ready_returns_200_when_db_connected(self, api_client, db):
        resp = api_client.get("/api/health/ready/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["database"] == "connected"

    def test_ready_returns_503_when_db_unavailable(self, api_client):
        with patch.object(connection, "ensure_connection") as mock:
            mock.side_effect = OperationalError("db gone")
            resp = api_client.get("/api/health/ready/")
        assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert resp.data["database"] == "disconnected"
