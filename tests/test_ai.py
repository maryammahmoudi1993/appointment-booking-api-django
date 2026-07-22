from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from rest_framework import status

from apps.ai.models import BookingDraft, Conversation, Message
from apps.ai.tools import (
    TOOL_DEFINITIONS,
    TOOL_MAP,
    execute_confirm_booking_draft,
    execute_confirm_cancellation,
    execute_create_booking_draft,
    execute_create_cancellation_draft,
    execute_create_reschedule_draft,
    execute_find_available_slots,
    execute_get_appointments,
    execute_get_booking_draft,
    execute_get_business_info,
    execute_get_service_details,
    execute_search_services,
    execute_suggest_staff,
    execute_tool,
    get_openai_tools,
)
from apps.staff.models import StaffProfile
from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ServiceFactory,
    StaffFactory,
    StaffProfileFactory,
    WorkingHoursFactory,
)

# ────────────────────────────────────────────────────────────────
# Tool Registry
# ────────────────────────────────────────────────────────────────


class TestToolRegistry:
    EXPECTED_TOOLS = {
        "search_services", "get_service_details", "get_staff", "suggest_staff",
        "find_available_slots", "get_appointments", "get_business_info",
        "create_booking_draft", "get_booking_draft", "confirm_booking_draft",
        "create_reschedule_draft", "confirm_reschedule",
        "create_cancellation_draft", "confirm_cancellation",
    }

    def test_all_tools_registered(self):
        assert set(TOOL_MAP.keys()) == self.EXPECTED_TOOLS

    def test_tool_count(self):
        assert len(TOOL_DEFINITIONS) == 14

    def test_every_tool_has_required_keys(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "execute" in tool
            assert callable(tool["execute"])

    def test_get_openai_tools_format(self):
        tools = get_openai_tools()
        assert len(tools) == 14
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
        result, error = execute_tool("search_services", user=customer)
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
# search_services
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSearchServices:
    def test_returns_all_services(self, customer):
        ServiceFactory.create_batch(3)
        result = execute_search_services(user=customer)
        assert len(result["services"]) == 3

    def test_filters_by_query(self, customer):
        ServiceFactory(name="Haircut")
        ServiceFactory(name="Manicure")
        result = execute_search_services(user=customer, query="Hair")
        assert len(result["services"]) == 1
        assert result["services"][0]["name"] == "Haircut"

    def test_filters_by_category(self, customer):
        ServiceFactory(category="hair")
        ServiceFactory(category="nails")
        result = execute_search_services(user=customer, category="hair")
        assert len(result["services"]) == 1

    def test_excludes_inactive(self, customer):
        ServiceFactory(is_active=True)
        ServiceFactory(is_active=False)
        result = execute_search_services(user=customer)
        assert len(result["services"]) == 1


# ────────────────────────────────────────────────────────────────
# get_service_details
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetServiceDetails:
    def test_returns_service(self, customer):
        svc = ServiceFactory(name="Massage", duration_minutes=60, price="90.00")
        result = execute_get_service_details(user=customer, service_id=svc.id)
        assert result["name"] == "Massage"
        assert result["duration_minutes"] == 60
        assert result["price"] == "90.00"

    def test_missing_service_id(self, customer):
        result = execute_get_service_details(user=customer)
        assert "error" in result

    def test_nonexistent_service(self, customer):
        result = execute_get_service_details(user=customer, service_id=99999)
        assert "error" in result


# ────────────────────────────────────────────────────────────────
# suggest_staff
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSuggestStaff:
    def test_returns_staff_for_service(self, customer):
        svc = ServiceFactory()
        sp = StaffProfileFactory()
        sp.services_offered.add(svc)
        result = execute_suggest_staff(user=customer, service_id=svc.id)
        assert len(result["staff"]) == 1
        assert result["staff"][0]["id"] == sp.user_id

    def test_missing_service_id(self, customer):
        result = execute_suggest_staff(user=customer)
        assert "error" in result


# ────────────────────────────────────────────────────────────────
# find_available_slots
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestFindAvailableSlots:
    def test_returns_slots(self):
        staff_user = StaffFactory()
        StaffProfile.objects.get_or_create(user=staff_user)
        svc = ServiceFactory(duration_minutes=30)
        sp = StaffProfile.objects.get(user=staff_user)
        sp.services_offered.add(svc)
        WorkingHoursFactory(staff=staff_user, weekday=0, start_time="09:00", end_time="10:00")
        target = _next_weekday(0)
        result = execute_find_available_slots(
            service_id=svc.id, date=target.isoformat(), user=None
        )
        assert "results" in result
        assert len(result["results"]) >= 1
        assert result["results"][0]["total_available"] > 0

    def test_missing_required_params(self):
        result = execute_find_available_slots(user=None)
        assert "error" in result

    def test_invalid_date(self):
        svc = ServiceFactory()
        result = execute_find_available_slots(
            service_id=svc.id, date="bad-date", user=None
        )
        assert "error" in result

    def test_nonexistent_service(self):
        result = execute_find_available_slots(
            service_id=99999, date="2026-01-01", user=None
        )
        assert "error" in result


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
# Booking draft creation
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreateBookingDraft:
    def _setup_booking_context(self, customer):
        staff_user = StaffFactory()
        StaffProfile.objects.get_or_create(user=staff_user)
        svc = ServiceFactory(duration_minutes=30, price="50.00")
        sp = StaffProfile.objects.get(user=staff_user)
        sp.services_offered.add(svc)
        WorkingHoursFactory(staff=staff_user, weekday=0, start_time="09:00", end_time="17:00")
        target = _next_weekday(0)
        return staff_user, svc, target

    def test_creates_draft(self, customer):
        staff_user, svc, target = self._setup_booking_context(customer)
        result = execute_create_booking_draft(
            user=customer,
            service_id=svc.id,
            staff_id=staff_user.id,
            date=target.isoformat(),
            start_time="10:00",
        )
        assert "draft_id" in result
        assert result["service"] == svc.name
        assert result["start_time"] == "10:00"
        assert result["expires_in_minutes"] == 15

    def test_requires_authentication(self):
        anon = MagicMock(is_authenticated=False)
        result = execute_create_booking_draft(
            user=anon, service_id=1, staff_id=1, date="2026-01-01", start_time="10:00"
        )
        assert "error" in result

    def test_missing_params(self, customer):
        result = execute_create_booking_draft(user=customer)
        assert "error" in result

    def test_nonexistent_service(self, customer):
        staff = StaffFactory()
        result = execute_create_booking_draft(
            user=customer, service_id=99999, staff_id=staff.id,
            date="2026-01-01", start_time="10:00"
        )
        assert "error" in result

    def test_creates_draft_record_in_db(self, customer):
        staff_user, svc, target = self._setup_booking_context(customer)
        execute_create_booking_draft(
            user=customer, service_id=svc.id, staff_id=staff_user.id,
            date=target.isoformat(), start_time="10:00"
        )
        assert BookingDraft.objects.filter(user=customer).count() == 1


# ────────────────────────────────────────────────────────────────
# Booking draft confirmation
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestConfirmBookingDraft:
    def _create_draft(self, customer):
        staff_user = StaffFactory()
        StaffProfile.objects.get_or_create(user=staff_user)
        svc = ServiceFactory(duration_minutes=30, price="50.00")
        sp = StaffProfile.objects.get(user=staff_user)
        sp.services_offered.add(svc)
        WorkingHoursFactory(staff=staff_user, weekday=0, start_time="09:00", end_time="17:00")
        target = _next_weekday(0)
        result = execute_create_booking_draft(
            user=customer, service_id=svc.id, staff_id=staff_user.id,
            date=target.isoformat(), start_time="10:00"
        )
        return result["draft_id"]

    def test_confirms_draft_creates_appointment(self, customer):
        draft_id = self._create_draft(customer)
        result = execute_confirm_booking_draft(user=customer, draft_id=draft_id)
        assert result["success"] is True
        assert "appointment_id" in result
        assert result["status"] == "pending"

    def test_expired_draft_fails(self, customer):
        staff_user = StaffFactory()
        StaffProfile.objects.get_or_create(user=staff_user)
        svc = ServiceFactory(duration_minutes=30)
        _next_weekday(0)
        draft = BookingDraft.objects.create(
            user=customer, service=svc, staff=staff_user,
            start_datetime=timezone.now() + timedelta(days=30, hours=10),
            end_datetime=timezone.now() + timedelta(days=30, hours=10, minutes=30),
            price=svc.price,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        result = execute_confirm_booking_draft(user=customer, draft_id=str(draft.id))
        assert "error" in result
        assert "expired" in result["error"]

    def test_already_confirmed_draft_fails(self, customer):
        draft_id = self._create_draft(customer)
        execute_confirm_booking_draft(user=customer, draft_id=draft_id)
        result = execute_confirm_booking_draft(user=customer, draft_id=draft_id)
        assert "error" in result

    def test_wrong_user_cannot_confirm(self, customer):
        draft_id = self._create_draft(customer)
        other = CustomerFactory()
        result = execute_confirm_booking_draft(user=other, draft_id=draft_id)
        assert "error" in result

    def test_missing_draft_id(self, customer):
        result = execute_confirm_booking_draft(user=customer, draft_id=None)
        assert "error" in result


# ────────────────────────────────────────────────────────────────
# get_booking_draft
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetBookingDraft:
    def test_returns_draft_details(self, customer):
        staff_user = StaffFactory()
        StaffProfileFactory(user=staff_user)
        svc = ServiceFactory(name="Facial", price="75.00")
        draft = BookingDraft.objects.create(
            user=customer, service=svc, staff=staff_user,
            start_datetime=timezone.now() + timedelta(days=1, hours=10),
            end_datetime=timezone.now() + timedelta(days=1, hours=11),
            price=svc.price,
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        result = execute_get_booking_draft(user=customer, draft_id=str(draft.id))
        assert result["service"] == "Facial"
        assert result["status"] == "pending"
        assert result["is_expired"] is False

    def test_expired_draft_shows_expired(self, customer):
        staff_user = StaffFactory()
        svc = ServiceFactory()
        draft = BookingDraft.objects.create(
            user=customer, service=svc, staff=staff_user,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, minutes=30),
            price=svc.price,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        result = execute_get_booking_draft(user=customer, draft_id=str(draft.id))
        assert result["is_expired"] is True
        assert result["status"] == "expired"

    def test_nonexistent_draft(self, customer):
        result = execute_get_booking_draft(user=customer, draft_id="00000000-0000-0000-0000-000000000000")
        assert "error" in result


# ────────────────────────────────────────────────────────────────
# Cancellation draft
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCancellationDraft:
    def test_creates_cancellation_draft(self, customer):
        appt = AppointmentFactory(customer=customer, status="confirmed")
        result = execute_create_cancellation_draft(
            user=customer, appointment_id=appt.id
        )
        assert "draft_id" in result
        assert result["appointment_id"] == appt.id

    def test_confirm_cancellation(self, customer):
        appt = AppointmentFactory(customer=customer, status="confirmed")
        draft_result = execute_create_cancellation_draft(
            user=customer, appointment_id=appt.id
        )
        result = execute_confirm_cancellation(
            user=customer, draft_id=draft_result["draft_id"]
        )
        assert result["success"] is True
        appt.refresh_from_db()
        assert appt.status == "cancelled"

    def test_cannot_cancel_completed(self, customer):
        appt = AppointmentFactory(customer=customer, status="completed")
        result = execute_create_cancellation_draft(
            user=customer, appointment_id=appt.id
        )
        assert "error" in result


# ────────────────────────────────────────────────────────────────
# Reschedule draft
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRescheduleDraft:
    def test_creates_reschedule_draft(self, customer):
        staff_user = StaffFactory()
        StaffProfile.objects.get_or_create(user=staff_user)
        svc = ServiceFactory(duration_minutes=30)
        WorkingHoursFactory(staff=staff_user, weekday=0, start_time="09:00", end_time="17:00")
        appt = AppointmentFactory(customer=customer, staff=staff_user, service=svc, status="confirmed")
        target = _next_weekday(1)
        result = execute_create_reschedule_draft(
            user=customer, appointment_id=appt.id,
            new_date=target.isoformat(), new_start_time="11:00"
        )
        assert "draft_id" in result
        assert result["original_appointment_id"] == appt.id


# ────────────────────────────────────────────────────────────────
# Conversation model
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestConversationModel:
    def test_creates_conversation(self, customer):
        conv = Conversation.objects.create(user=customer)
        assert conv.id is not None
        assert conv.user == customer

    def test_message_creation(self, customer):
        conv = Conversation.objects.create(user=customer)
        msg = Message.objects.create(
            conversation=conv, role="user", content="Hello"
        )
        assert msg.id is not None
        assert conv.messages.count() == 1


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
        tool_call.function.name = "search_services"
        tool_call.function.arguments = "{}"

        assistant_msg = MagicMock()
        assistant_msg.content = None
        assistant_msg.tool_calls = [tool_call]

        final_msg = MagicMock()
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
        assert result.tool_calls_made[0]["tool"] == "search_services"

    @patch("apps.ai.copilot._get_client")
    def test_conversation_persisted(self, mock_get_client, customer, settings):
        settings.OPENAI_API_KEY = "sk-test"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_msg = MagicMock()
        mock_msg.content = "Hello!"
        mock_msg.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.message = mock_msg

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        from apps.ai.copilot import chat

        result = chat("Hi", user=customer)
        assert result.conversation_id is not None
        conv = Conversation.objects.get(id=result.conversation_id)
        assert conv.user == customer
        assert conv.messages.count() >= 2

    @patch("apps.ai.copilot._get_client")
    def test_max_rounds_exceeded(self, mock_get_client, db, settings):
        settings.OPENAI_API_KEY = "sk-test"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        tool_call = MagicMock()
        tool_call.id = "call_loop"
        tool_call.function.name = "search_services"
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
        assert len(result.tool_calls_made) == 8


# ────────────────────────────────────────────────────────────────
# Copilot API view
# ────────────────────────────────────────────────────────────────


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
    def test_returns_conversation_id(self, mock_chat, auth_client):
        from apps.ai.copilot import CopilotResponse

        mock_chat.return_value = CopilotResponse(
            reply="Hello!", tool_calls_made=[], conversation_id="abc-123"
        )
        response = auth_client.post(
            "/api/copilot/", {"message": "Hi"}, format="json"
        )
        assert response.data["conversation_id"] == "abc-123"

    @patch("apps.ai.views.chat")
    def test_passes_conversation_id(self, mock_chat, auth_client):
        import uuid

        from apps.ai.copilot import CopilotResponse

        test_uuid = str(uuid.uuid4())
        mock_chat.return_value = CopilotResponse(reply="OK", tool_calls_made=[])
        auth_client.post(
            "/api/copilot/",
            {"message": "Hi", "conversation_id": test_uuid},
            format="json",
        )
        mock_chat.assert_called_once()
        _, kwargs = mock_chat.call_args
        assert kwargs["conversation_id"] == uuid.UUID(test_uuid)

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


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────


def _next_weekday(weekday):
    today = timezone.now().date()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)
