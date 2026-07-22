from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from rest_framework import status

from apps.ai.tools import (
    TOOL_DEFINITIONS,
    TOOL_MAP,
    execute_get_appointments,
    execute_get_available_slots,
    execute_get_business_info,
    execute_get_services,
    execute_get_staff,
    execute_tool,
    get_openai_tools,
)
from tests.factories import (
    AppointmentFactory,
    ServiceFactory,
    StaffFactory,
    StaffProfileFactory,
    WorkingHoursFactory,
)

# ────────────────────────────────────────────────────────────────
# Tool Registry
# ────────────────────────────────────────────────────────────────


class TestToolRegistry:
    def test_all_tools_registered(self):
        expected = {"get_services", "get_staff", "get_available_slots", "get_appointments", "get_business_info"}
        assert set(TOOL_MAP.keys()) == expected

    def test_every_tool_has_required_keys(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "execute" in tool
            assert callable(tool["execute"])

    def test_get_openai_tools_format(self):
        tools = get_openai_tools()
        assert len(tools) == 5
        for t in tools:
            assert t["type"] == "function"
            assert "name" in t["function"]
            assert "description" in t["function"]
            assert "parameters" in t["function"]


# ────────────────────────────────────────────────────────────────
# execute_tool dispatcher
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestExecuteTool:
    def test_execute_known_tool(self, customer):
        result, error = execute_tool("get_services", user=customer)
        assert error is None
        assert "services" in result

    def test_execute_unknown_tool(self, customer):
        result, error = execute_tool("nonexistent_tool", user=customer)
        assert result is None
        assert "Unknown tool" in error

    def test_execute_tool_exception(self, customer):
        with patch.dict(TOOL_MAP, {"boom": {"execute": lambda **kw: 1 / 0}}):
            result, error = execute_tool("boom", user=customer)
            assert result is None
            assert "Tool execution error" in error


# ────────────────────────────────────────────────────────────────
# get_services
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetServices:
    def test_returns_services(self, customer):
        ServiceFactory.create_batch(3)
        result = execute_get_services(user=customer)
        assert len(result["services"]) == 3

    def test_filters_by_category(self, customer):
        ServiceFactory(category="hair")
        ServiceFactory(category="nails")
        result = execute_get_services(user=customer, category="hair")
        assert len(result["services"]) == 1
        assert result["services"][0]["category"] == "hair"

    def test_excludes_inactive(self, customer):
        ServiceFactory(is_active=True)
        ServiceFactory(is_active=False)
        result = execute_get_services(user=customer)
        assert len(result["services"]) == 1

    def test_service_serialization(self, customer):
        ServiceFactory(name="Haircut", duration_minutes=45, price="75.00")
        result = execute_get_services(user=customer)
        svc = result["services"][0]
        assert svc["name"] == "Haircut"
        assert svc["duration_minutes"] == 45
        assert svc["price"] == "75.00"


# ────────────────────────────────────────────────────────────────
# get_staff
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetStaff:
    def test_returns_staff(self, customer):
        StaffProfileFactory()
        StaffProfileFactory()
        result = execute_get_staff(user=customer)
        assert len(result["staff"]) == 2

    def test_filters_by_service_name(self, customer):
        svc = ServiceFactory(name="Massage")
        sp = StaffProfileFactory()
        sp.services_offered.add(svc)
        StaffProfileFactory()
        result = execute_get_staff(user=customer, service_name="Massage")
        assert len(result["staff"]) == 1

    def test_staff_serialization(self, customer):
        sp = StaffProfileFactory()
        result = execute_get_staff(user=customer)
        staff = result["staff"][0]
        assert staff["id"] == sp.user_id
        assert "name" in staff
        assert "services" in staff


# ────────────────────────────────────────────────────────────────
# get_available_slots
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetAvailableSlots:
    def test_returns_slots(self):
        staff_user = StaffFactory()
        StaffProfileFactory(user=staff_user)
        WorkingHoursFactory(staff=staff_user, weekday=0, start_time="09:00", end_time="10:00")
        target = self._next_weekday(0)
        result = execute_get_available_slots(staff_id=staff_user.id, date=target.isoformat(), user=None)
        assert result["total_available"] > 0
        assert result["date"] == target.isoformat()

    def test_no_working_hours_returns_empty(self):
        staff_user = StaffFactory()
        target = self._next_weekday(0)
        result = execute_get_available_slots(staff_id=staff_user.id, date=target.isoformat(), user=None)
        assert result["total_available"] == 0

    def test_invalid_date_format(self):
        result = execute_get_available_slots(staff_id=999, date="not-a-date", user=None)
        assert "error" in result

    def _next_weekday(self, weekday):
        today = timezone.now().date()
        days_ahead = (weekday - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)


# ────────────────────────────────────────────────────────────────
# get_appointments
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetAppointments:
    def test_returns_customer_appointments(self, customer):
        AppointmentFactory(customer=customer, status="confirmed")
        AppointmentFactory(customer=customer, status="pending")
        result = execute_get_appointments(user=customer)
        assert len(result["appointments"]) == 2

    def test_requires_authentication(self):
        anon = MagicMock(is_authenticated=False)
        result = execute_get_appointments(user=anon)
        assert "error" in result

    def test_filters_by_status(self, customer):
        AppointmentFactory(customer=customer, status="confirmed")
        AppointmentFactory(customer=customer, status="pending")
        result = execute_get_appointments(user=customer, status="confirmed")
        assert len(result["appointments"]) == 1

    def test_excludes_cancelled(self, customer):
        AppointmentFactory(customer=customer, status="cancelled")
        result = execute_get_appointments(user=customer)
        assert len(result["appointments"]) == 0

    def test_appointment_serialization(self, customer):
        a = AppointmentFactory(customer=customer, status="confirmed")
        result = execute_get_appointments(user=customer)
        appt = result["appointments"][0]
        assert appt["id"] == a.id
        assert appt["status"] == "confirmed"
        assert "start" in appt
        assert "service" in appt


# ────────────────────────────────────────────────────────────────
# get_business_info
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetBusinessInfo:
    def test_returns_business_info(self, customer):
        result = execute_get_business_info(user=customer)
        assert "name" in result
        assert "timezone" in result

    def test_no_business_returns_error(self):
        anon = MagicMock(is_authenticated=False)
        with patch("apps.ai.tools._get_business", return_value=None):
            result = execute_get_business_info(user=anon)
            assert "error" in result


# ────────────────────────────────────────────────────────────────
# Copilot service
# ────────────────────────────────────────────────────────────────


class TestCopilotService:
    def test_fallback_when_no_api_key(self, settings):
        settings.OPENAI_API_KEY = None
        from apps.ai.copilot import chat

        result = chat("Hello", user=None)
        assert "not configured" in result.reply

    @patch("apps.ai.copilot._get_client")
    def test_simple_text_response(self, mock_get_client, settings):
        settings.OPENAI_API_KEY = "sk-test"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_msg = MagicMock()
        mock_msg.content = "Hello! How can I help?"
        mock_msg.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.message = mock_msg

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        from apps.ai.copilot import chat

        result = chat("Hi", user=None)
        assert result.reply == "Hello! How can I help?"
        assert result.tool_calls_made == []

    @patch("apps.ai.copilot._get_client")
    def test_tool_calling_loop(self, mock_get_client, customer, settings):
        settings.OPENAI_API_KEY = "sk-test"
        ServiceFactory.create_batch(2)
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "get_services"
        tool_call.function.arguments = "{}"

        assistant_msg = MagicMock()
        assistant_msg.content = None
        assistant_msg.tool_calls = [tool_call]

        final_msg = MagicMock()
        assistant_msg.tool_calls = [tool_call]
        final_msg.content = "We offer 2 services!"
        final_msg.tool_calls = None

        mock_choice1 = MagicMock()
        mock_choice1.message = assistant_msg
        mock_choice2 = MagicMock()
        mock_choice2.message = final_msg

        mock_response1 = MagicMock()
        mock_response1.choices = [mock_choice1]
        mock_response2 = MagicMock()
        mock_response2.choices = [mock_choice2]

        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]

        from apps.ai.copilot import chat

        result = chat("What services do you offer?", user=customer)
        assert result.reply == "We offer 2 services!"
        assert len(result.tool_calls_made) == 1
        assert result.tool_calls_made[0]["tool"] == "get_services"

    @patch("apps.ai.copilot._get_client")
    def test_max_rounds_exceeded(self, mock_get_client, db, settings):
        settings.OPENAI_API_KEY = "sk-test"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        tool_call = MagicMock()
        tool_call.id = "call_loop"
        tool_call.function.name = "get_services"
        tool_call.function.arguments = "{}"

        loop_msg = MagicMock()
        loop_msg.content = None
        loop_msg.tool_calls = [tool_call]

        mock_choice = MagicMock()
        mock_choice.message = loop_msg

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        from apps.ai.copilot import chat

        result = chat("loop", user=None)
        assert len(result.tool_calls_made) == 5


# ────────────────────────────────────────────────────────────────
# Copilot API view
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.django_db
class TestCopilotView:
    def test_unauthenticated_gets_401(self, api_client):
        response = api_client.post("/api/copilot/", {"message": "Hi"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.ai.views.chat")
    def test_authenticated_post_returns_reply(self, mock_chat, auth_client):
        from apps.ai.copilot import CopilotResponse

        mock_chat.return_value = CopilotResponse(reply="Hello!", tool_calls_made=[])
        response = auth_client.post(
            "/api/copilot/", {"message": "Hi"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["reply"] == "Hello!"

    @patch("apps.ai.views.chat")
    def test_returns_tool_calls_made(self, mock_chat, auth_client):
        from apps.ai.copilot import CopilotResponse

        mock_chat.return_value = CopilotResponse(
            reply="Here are the services.",
            tool_calls_made=[{"tool": "get_services", "args": {}}],
        )
        response = auth_client.post(
            "/api/copilot/", {"message": "Show services"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["tool_calls_made"]) == 1

    def test_empty_message_rejected(self, auth_client):
        response = auth_client.post("/api/copilot/", {"message": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_message_rejected(self, auth_client):
        response = auth_client.post("/api/copilot/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_message_too_long_rejected(self, auth_client):
        response = auth_client.post(
            "/api/copilot/", {"message": "x" * 2001}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
