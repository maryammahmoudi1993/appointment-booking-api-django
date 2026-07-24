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
    execute_predict_no_show,
    execute_recommend_services,
    execute_search_services,
    execute_suggest_staff,
    execute_tool,
    get_tool_declarations,
)
from apps.staff.models import StaffProfile
from tests.factories import (
    AppointmentFactory,
    CustomerFactory,
    ReviewFactory,
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
        "recommend_services", "predict_no_show", "forecast_revenue",
        "get_revenue_analytics", "get_staff_analytics", "get_service_analytics",
        "get_booking_analytics", "get_top_services", "get_staff_performance",
    }

    def test_all_tools_registered(self):
        assert set(TOOL_MAP.keys()) == self.EXPECTED_TOOLS

    def test_tool_count(self):
        assert len(TOOL_DEFINITIONS) == 23

    def test_every_tool_has_required_keys(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "execute" in tool
            assert callable(tool["execute"])

    def test_get_tool_declarations_format(self):
        tools = get_tool_declarations()
        assert len(tools) == 23
        for t in tools:
            assert "name" in t
            assert "description" in t
            assert "parameters" in t


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


def _gemini_text_response(text):
    """Build a MagicMock shaped like a Gemini generate_content() response
    with no function calls — just a final text reply."""
    mock_response = MagicMock()
    mock_response.text = text
    mock_response.candidates[0].content.parts = []
    return mock_response


def _gemini_function_call_response(name, args):
    """Build a MagicMock shaped like a Gemini generate_content() response
    containing a single function call part."""
    mock_part = MagicMock()
    mock_part.function_call.name = name
    mock_part.function_call.args = args
    mock_response = MagicMock()
    mock_response.candidates[0].content.parts = [mock_part]
    return mock_response


class TestCopilotService:
    def test_fallback_when_no_api_key(self, settings):
        settings.GEMINI_API_KEY = None
        from apps.ai.copilot import chat

        result = chat("Hello", user=None)
        assert "not configured" in result.reply

    @patch("apps.ai.copilot._get_client")
    def test_provider_error_returns_graceful_fallback_not_500(self, mock_get_client, settings):
        """Regression test: an invalid/rejected API key, rate limit, or any
        other Gemini SDK exception used to propagate uncaught all the way
        to an Internal Server Error. It must now degrade to a friendly
        CopilotResponse instead."""
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "Error code: 401 - invalid_api_key"
        )

        from apps.ai.copilot import chat

        result = chat("Hi", user=None)
        assert "trouble reaching" in result.reply
        assert "401" not in result.reply

    @patch("apps.ai.copilot._get_client")
    def test_simple_text_response(self, mock_get_client, settings):
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.return_value = _gemini_text_response(
            "Hello! How can I help?"
        )

        from apps.ai.copilot import chat

        result = chat("Hi", user=None)
        assert result.reply == "Hello! How can I help?"
        assert result.tool_calls_made == []

    @patch("apps.ai.copilot._get_client")
    def test_tool_calling_loop(self, mock_get_client, customer, settings):
        settings.GEMINI_API_KEY = "test-key"
        ServiceFactory.create_batch(2)
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.models.generate_content.side_effect = [
            _gemini_function_call_response("search_services", {}),
            _gemini_text_response("We offer 2 services!"),
        ]

        from apps.ai.copilot import chat

        result = chat("What services do you offer?", user=customer)
        assert result.reply == "We offer 2 services!"
        assert len(result.tool_calls_made) == 1
        assert result.tool_calls_made[0]["tool"] == "search_services"

    @patch("apps.ai.copilot._get_client")
    def test_conversation_persisted(self, mock_get_client, customer, settings):
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.return_value = _gemini_text_response("Hello!")

        from apps.ai.copilot import chat

        result = chat("Hi", user=customer)
        assert result.conversation_id is not None
        conv = Conversation.objects.get(id=result.conversation_id)
        assert conv.user == customer
        assert conv.messages.count() >= 2

    @patch("apps.ai.copilot._get_client")
    def test_max_rounds_exceeded(self, mock_get_client, db, settings):
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.return_value = _gemini_function_call_response(
            "search_services", {}
        )

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
# Admin Copilot View
# ────────────────────────────────────────────────────────────────


class TestAdminCopilotView:
    def test_unauthenticated_gets_401(self, client):
        response = client.post("/api/admin/copilot/", {"message": "Hi"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_gets_403(self, auth_client):
        response = auth_client.post("/api/admin/copilot/", {"message": "Hi"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("apps.ai.views.admin_chat")
    def test_admin_post_returns_reply(self, mock_chat, admin_client):
        from apps.ai.admin_copilot import AdminCopilotResponse

        mock_chat.return_value = AdminCopilotResponse(reply="Revenue is up", tool_calls_made=[])
        response = admin_client.post("/api/admin/copilot/", {"message": "Show revenue"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "reply" in response.json()
        mock_chat.assert_called_once()

    @patch("apps.ai.views.admin_chat")
    def test_empty_message_rejected(self, mock_chat, admin_client):
        response = admin_client.post("/api/admin/copilot/", {"message": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_view_passes_authenticated_user_to_admin_chat(self, admin_client, admin_user):
        """Regression test: the view must forward request.user into admin_chat
        so tool calls resolve to the requesting admin's own business, not the
        globally-first active business (see apps/ai/admin_copilot.py)."""
        with patch("apps.ai.views.admin_chat") as mock_chat:
            from apps.ai.admin_copilot import AdminCopilotResponse

            mock_chat.return_value = AdminCopilotResponse(reply="ok", tool_calls_made=[])
            admin_client.post("/api/admin/copilot/", {"message": "Show revenue"}, format="json")

            _, kwargs = mock_chat.call_args
            assert kwargs.get("user") == admin_user

    @patch("google.genai.Client")
    def test_admin_chat_provider_error_returns_graceful_fallback(self, mock_client_cls, settings):
        """Regression test: a Gemini SDK exception (invalid key, rate limit,
        network error) used to propagate uncaught to a 500 in admin_chat()
        too. Must degrade to a friendly AdminCopilotResponse instead."""
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "Error code: 401 - invalid_api_key"
        )

        from apps.ai.admin_copilot import admin_chat

        result = admin_chat("Show revenue", user=None)
        assert "trouble reaching" in result.reply
        assert "401" not in result.reply

    @patch("google.genai.Client")
    def test_admin_chat_reports_provider_quota_exhaustion(self, mock_client_cls, settings):
        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        quota_error = Exception("429 RESOURCE_EXHAUSTED")
        quota_error.status_code = 429
        mock_client.models.generate_content.side_effect = quota_error

        from apps.ai.admin_copilot import admin_chat

        result = admin_chat("Show revenue", user=None)
        assert "quota is currently exhausted" in result.reply
        assert "429" not in result.reply

    @pytest.mark.django_db
    @patch("google.genai.Client")
    def test_admin_chat_resolves_requesting_admins_own_business(self, mock_client_cls, settings):
        """Regression test for the cross-tenant leak: two businesses each with
        their own admin and their own completed appointment revenue. Business
        A is created first (so it is "the first active business"), Business B
        second. Business B's admin asking for revenue analytics must see
        Business B's numbers, not Business A's, via a real user-scoped call."""
        from decimal import Decimal

        from apps.business.models import Business, BusinessMembership

        business_a = Business.objects.create(name="Salon A", slug="salon-a")
        business_b = Business.objects.create(name="Salon B", slug="salon-b")

        admin_b = StaffFactory()
        admin_b.role = "admin"
        admin_b.save()
        BusinessMembership.objects.create(
            user=admin_b, business=business_b, role="admin"
        )

        service_a = ServiceFactory(business=business_a, price=Decimal("100.00"))
        staff_a = StaffFactory()
        AppointmentFactory(
            business=business_a,
            staff=staff_a,
            service=service_a,
            status="completed",
        )

        service_b = ServiceFactory(business=business_b, price=Decimal("250.00"))
        staff_b = StaffFactory()
        AppointmentFactory(
            business=business_b,
            staff=staff_b,
            service=service_b,
            status="completed",
        )

        settings.GEMINI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = [
            _gemini_function_call_response("get_revenue_analytics", {}),
            _gemini_text_response("done"),
        ]

        from apps.ai.admin_copilot import admin_chat

        admin_chat("Show revenue", user=admin_b)

        second_call_contents = mock_client.models.generate_content.call_args_list[1].kwargs[
            "contents"
        ]
        function_response_content = second_call_contents[-1]
        tool_result = function_response_content.parts[0].function_response.response
        assert "250" in str(tool_result)
        assert "100" not in str(tool_result)


# ────────────────────────────────────────────────────────────────
# Service Recommendation Engine
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRecommenderHistoryScore:
    def test_no_history_returns_zero(self):
        from apps.ai.recommender import _history_scores

        customer = CustomerFactory()
        svc = ServiceFactory()
        scores = _history_scores(customer.id, svc.business_id)
        assert scores.get(svc.id, 0.0) == 0.0

    def test_booked_service_scores_higher(self):
        from apps.ai.recommender import _history_scores

        customer = CustomerFactory()
        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            customer=customer,
            staff=staff_user,
            service=svc,
            status="completed",
        )
        scores = _history_scores(customer.id, svc.business_id)
        assert scores.get(svc.id, 0.0) > 0.0

    def test_multiple_bookings_normalised(self):
        from apps.ai.recommender import _history_scores

        customer = CustomerFactory()
        svc_a = ServiceFactory()
        svc_b = ServiceFactory(business=svc_a.business)
        staff_user = StaffFactory()

        for _ in range(3):
            AppointmentFactory(
                customer=customer, staff=staff_user, service=svc_a, status="completed"
            )
        AppointmentFactory(
            customer=customer, staff=staff_user, service=svc_b, status="completed"
        )

        scores = _history_scores(customer.id, svc_a.business_id)
        assert scores[svc_a.id] == 1.0
        assert scores[svc_b.id] == pytest.approx(1 / 3, abs=0.01)


@pytest.mark.django_db
class TestRecommenderRatingScore:
    def test_no_reviews_returns_zero(self):
        from apps.ai.recommender import _rating_scores

        svc = ServiceFactory()
        scores = _rating_scores(svc.business_id)
        assert scores.get(svc.id, 0.0) == 0.0

    def test_reviewed_service_scores_higher(self):
        from apps.ai.recommender import _rating_scores

        svc = ServiceFactory()
        staff_user = StaffFactory()
        appt = AppointmentFactory(staff=staff_user, service=svc, status="completed")
        ReviewFactory(appointment=appt, staff=staff_user, rating=4)

        scores = _rating_scores(svc.business_id)
        assert scores[svc.id] == pytest.approx(4 / 5, abs=0.01)


@pytest.mark.django_db
class TestRecommenderPopularityScore:
    def test_more_bookings_higher_score(self):
        from apps.ai.recommender import _popularity_scores

        svc_a = ServiceFactory()
        svc_b = ServiceFactory(business=svc_a.business)
        staff_user = StaffFactory()

        for _ in range(5):
            AppointmentFactory(
                staff=staff_user, service=svc_a, status="completed"
            )
        AppointmentFactory(
            staff=staff_user, service=svc_b, status="completed"
        )

        scores = _popularity_scores(svc_a.business_id)
        assert scores[svc_a.id] == 1.0
        assert scores[svc_b.id] == pytest.approx(0.2, abs=0.01)


@pytest.mark.django_db
class TestRecommenderRecencyScore:
    def test_recent_booking_scores_higher(self):
        from apps.ai.recommender import _recency_scores

        customer = CustomerFactory()
        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            customer=customer,
            staff=staff_user,
            service=svc,
            status="completed",
            start_datetime=timezone.now() - timedelta(days=1),
        )

        scores = _recency_scores(customer.id, svc.business_id)
        assert scores.get(svc.id, 0.0) > 0.8

    def test_old_booking_scores_lower(self):
        from apps.ai.recommender import _recency_scores

        customer = CustomerFactory()
        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            customer=customer,
            staff=staff_user,
            service=svc,
            status="completed",
            start_datetime=timezone.now() - timedelta(days=60),
        )

        scores = _recency_scores(customer.id, svc.business_id)
        assert 0.0 < scores.get(svc.id, 0.0) < 0.5


@pytest.mark.django_db
class TestRecommendServices:
    def test_returns_empty_when_no_services(self):
        from apps.ai.recommender import recommend_services

        results = recommend_services(business_id=99999)
        assert results == []

    def test_returns_active_services_only(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory(is_active=True)
        ServiceFactory(is_active=False, business=svc.business)
        results = recommend_services(business_id=svc.business_id, top_n=10)
        assert len(results) == 1
        assert results[0].service_id == svc.id

    def test_top_n_limits_results(self):
        from apps.ai.recommender import recommend_services

        for _ in range(10):
            ServiceFactory()
        results = recommend_services(top_n=3)
        assert len(results) == 3

    def test_sorted_by_score_desc(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(staff=staff_user, service=svc, status="completed")
        AppointmentFactory(staff=staff_user, service=svc, status="completed")
        ServiceFactory(business=svc.business)

        results = recommend_services(business_id=svc.business_id)
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_explanation_included(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory()
        results = recommend_services(business_id=svc.business_id, top_n=1)
        assert len(results) == 1
        assert isinstance(results[0].explanation, str)
        assert len(results[0].explanation) > 0

    def test_factors_present(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory()
        results = recommend_services(business_id=svc.business_id, top_n=1)
        factors = results[0].factors
        assert "history" in factors
        assert "rating" in factors
        assert "availability" in factors
        assert "popularity" in factors
        assert "recency" in factors

    def test_guest_user_no_history_recency(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory()
        results = recommend_services(customer_id=None, business_id=svc.business_id, top_n=1)
        assert len(results) == 1
        assert results[0].factors["history"] == 0.0
        assert results[0].factors["recency"] == 0.0

    def test_customer_with_bookings_gets_history_score(self):
        from apps.ai.recommender import recommend_services

        customer = CustomerFactory()
        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            customer=customer, staff=staff_user, service=svc, status="completed"
        )
        results = recommend_services(
            customer_id=customer.id, business_id=svc.business_id, top_n=5
        )
        svc_result = next((r for r in results if r.service_id == svc.id), None)
        assert svc_result is not None
        assert svc_result.factors["history"] > 0.0

    def test_custom_weights_affect_score(self):
        from apps.ai.recommender import recommend_services

        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            staff=staff_user, service=svc, status="completed"
        )

        results_default = recommend_services(business_id=svc.business_id, top_n=1)
        results_custom = recommend_services(
            business_id=svc.business_id,
            top_n=1,
            weights={"popularity": 1.0, "history": 0, "rating": 0, "availability": 0, "recency": 0},
        )
        assert results_default[0].total_score != results_custom[0].total_score


@pytest.mark.django_db
class TestExecuteRecommendServices:
    def test_returns_recommendations(self):
        ServiceFactory()
        result = execute_recommend_services(user=None, top_n=3)
        assert "recommendations" in result
        assert result["count"] <= 3

    def test_authenticated_user(self, customer):
        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(
            customer=customer, staff=staff_user, service=svc, status="completed"
        )
        result = execute_recommend_services(user=customer, top_n=5)
        assert result["count"] >= 1
        rec = result["recommendations"][0]
        assert "service_id" in rec
        assert "score" in rec
        assert "explanation" in rec

    def test_top_n_capped_at_20(self):
        result = execute_recommend_services(user=None, top_n=100)
        assert result["count"] <= 20

    def test_tool_in_registry(self):
        from apps.ai.tools import TOOL_MAP

        assert "recommend_services" in TOOL_MAP
        tool = TOOL_MAP["recommend_services"]
        assert "execute" in tool
        assert callable(tool["execute"])


# ────────────────────────────────────────────────────────────────
# No-Show Prediction Engine
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestNoShowPredictor:
    def test_build_feature_row(self):
        from apps.ai.no_show import _build_feature_row

        appt = AppointmentFactory(
            start_datetime=timezone.now() + timedelta(days=3),
        )
        row = _build_feature_row(appt)
        assert len(row) == 8
        assert isinstance(row[0], float)

    def test_synthetic_training_data_shape(self):
        from apps.ai.no_show import _generate_synthetic_training_data

        X, y = _generate_synthetic_training_data(n_samples=100)
        assert X.shape == (100, 8)
        assert y.shape == (100,)
        assert set(y.tolist()).issubset({0.0, 1.0})

    def test_predict_returns_prediction_result(self):
        from apps.ai.no_show import PredictionResult, predict_no_show

        appt = AppointmentFactory(
            start_datetime=timezone.now() + timedelta(days=1),
            status="confirmed",
        )
        result = predict_no_show(appt)
        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.probability_no_show <= 1.0
        assert result.risk_level in ("low", "medium", "high")
        assert "lead_time_days" in result.feature_contributions
        assert isinstance(result.explanation, str)

    def test_risk_level_thresholds(self):
        from apps.ai.no_show import predict_no_show

        appt = AppointmentFactory(
            start_datetime=timezone.now() + timedelta(days=14),
            status="confirmed",
        )
        result = predict_no_show(appt)
        assert result.risk_level in ("low", "medium", "high")

    def test_cancelled_appointment_training(self):
        from apps.ai.no_show import _build_training_data

        AppointmentFactory(status="cancelled")
        AppointmentFactory(status="completed")
        AppointmentFactory(status="completed")
        X, y = _build_training_data()
        assert len(X) >= 3
        assert 1.0 in y
        assert 0.0 in y


@pytest.mark.django_db
class TestExecutePredictNoShow:
    def test_returns_prediction(self):
        appt = AppointmentFactory(
            start_datetime=timezone.now() + timedelta(days=2),
            status="confirmed",
        )
        result = execute_predict_no_show(user=None, appointment_id=appt.id)
        assert "probability_no_show" in result
        assert "risk_level" in result
        assert "explanation" in result
        assert result["appointment_id"] == appt.id

    def test_nonexistent_appointment(self):
        result = execute_predict_no_show(user=None, appointment_id=99999)
        assert "error" in result

    def test_missing_appointment_id(self):
        result = execute_predict_no_show(user=None)
        assert "error" in result

    def test_includes_appointment_context(self):
        appt = AppointmentFactory(
            start_datetime=timezone.now() + timedelta(days=1),
            status="confirmed",
        )
        result = execute_predict_no_show(user=None, appointment_id=appt.id)
        assert result["customer"]
        assert result["service"]
        assert result["staff"]
        assert "T" in result["appointment_time"]

    def test_tool_in_registry(self):
        from apps.ai.tools import TOOL_MAP

        assert "predict_no_show" in TOOL_MAP
        tool = TOOL_MAP["predict_no_show"]
        assert "execute" in tool
        assert callable(tool["execute"])


# ────────────────────────────────────────────────────────────────
# Revenue Forecast Engine
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRevenueForecast:
    def test_empty_data_returns_empty(self):
        from apps.ai.revenue_forecast import forecast_revenue

        result = forecast_revenue(business_id=99999)
        assert result.forecast_points == []
        assert result.total_forecast == 0.0
        assert "No historical" in result.explanation

    def test_with_completed_appointments(self):
        from apps.ai.revenue_forecast import forecast_revenue

        svc = ServiceFactory(price="100.00")
        staff_user = StaffFactory()
        for _ in range(5):
            AppointmentFactory(
                staff=staff_user,
                service=svc,
                status="completed",
                start_datetime=timezone.now() - timedelta(days=10),
            )
        result = forecast_revenue(
            business_id=svc.business_id,
            forecast_days=7,
            granularity="daily",
        )
        assert len(result.forecast_points) == 7
        assert result.total_forecast > 0
        assert result.historical_avg_daily > 0

    def test_granularity_weekly(self):
        from apps.ai.revenue_forecast import forecast_revenue

        svc = ServiceFactory(price="50.00")
        staff_user = StaffFactory()
        for _ in range(3):
            AppointmentFactory(
                staff=staff_user,
                service=svc,
                status="completed",
            )
        result = forecast_revenue(
            business_id=svc.business_id,
            forecast_days=30,
            granularity="weekly",
        )
        assert result.granularity == "weekly"
        assert len(result.forecast_points) > 0

    def test_forecast_days_capped(self):
        from apps.ai.revenue_forecast import forecast_revenue

        svc = ServiceFactory()
        staff_user = StaffFactory()
        AppointmentFactory(staff=staff_user, service=svc, status="completed")
        result = forecast_revenue(
            business_id=svc.business_id,
            forecast_days=500,
        )
        assert len(result.forecast_points) <= 365

    def test_trend_detection(self):
        from apps.ai.revenue_forecast import forecast_revenue

        svc = ServiceFactory(price="100.00")
        staff_user = StaffFactory()
        for i in range(20):
            AppointmentFactory(
                staff=staff_user,
                service=svc,
                status="completed",
                start_datetime=timezone.now() - timedelta(days=20 - i),
            )
        result = forecast_revenue(
            business_id=svc.business_id,
            forecast_days=7,
        )
        assert result.trend in ("up", "down", "stable")
        assert isinstance(result.explanation, str)

    def test_bounds_increase_with_distance(self):
        from apps.ai.revenue_forecast import forecast_revenue

        svc = ServiceFactory(price="80.00")
        staff_user = StaffFactory()
        for _ in range(10):
            AppointmentFactory(
                staff=staff_user,
                service=svc,
                status="completed",
            )
        result = forecast_revenue(
            business_id=svc.business_id,
            forecast_days=14,
        )
        if len(result.forecast_points) >= 2:
            first = result.forecast_points[0]
            last = result.forecast_points[-1]
            first_width = first.upper_bound - first.lower_bound
            last_width = last.upper_bound - last.lower_bound
            assert last_width >= first_width


@pytest.mark.django_db
class TestExecuteForecastRevenue:
    def test_returns_forecast(self):
        from apps.ai.tools import execute_forecast_revenue

        result = execute_forecast_revenue(user=None)
        assert "forecast_points" in result
        assert "trend" in result
        assert "total_forecast" in result

    def test_with_completed_data(self):
        from apps.ai.tools import execute_forecast_revenue

        svc = ServiceFactory(price="120.00")
        staff_user = StaffFactory()
        AppointmentFactory(
            staff=staff_user, service=svc, status="completed"
        )
        result = execute_forecast_revenue(user=None, forecast_days=7)
        assert result["total_forecast"] > 0 or len(result["forecast_points"]) == 0

    def test_custom_granularity(self):
        from apps.ai.tools import execute_forecast_revenue

        result = execute_forecast_revenue(user=None, granularity="monthly")
        assert result["granularity"] == "monthly"

    def test_invalid_granularity_defaults(self):
        from apps.ai.tools import execute_forecast_revenue

        result = execute_forecast_revenue(user=None, granularity="invalid")
        assert result["granularity"] == "daily"

    def test_tool_in_registry(self):
        from apps.ai.tools import TOOL_MAP

        assert "forecast_revenue" in TOOL_MAP
        tool = TOOL_MAP["forecast_revenue"]
        assert "execute" in tool
        assert callable(tool["execute"])


# ────────────────────────────────────────────────────────────────
# Admin Analytics Tools
# ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminTools:
    def test_revenue_analytics_empty(self):
        from apps.ai.tools import execute_get_revenue_analytics

        result = execute_get_revenue_analytics(user=None)
        assert result["total_bookings"] == 0
        assert result["total_revenue"] == "0.00"
        assert result["average_ticket"] == "0.00"

    def test_staff_analytics_empty(self):
        from apps.ai.tools import execute_get_staff_analytics

        result = execute_get_staff_analytics(user=None)
        assert result["staff"] == []

    def test_service_analytics_empty(self):
        from apps.ai.tools import execute_get_service_analytics

        result = execute_get_service_analytics(user=None)
        assert result["services"] == []

    def test_booking_analytics_empty(self):
        from apps.ai.tools import execute_get_booking_analytics

        result = execute_get_booking_analytics(user=None)
        assert result["total"] == 0

    def test_top_services_empty(self):
        from apps.ai.tools import execute_get_top_services

        result = execute_get_top_services(user=None)
        assert result["services"] == []

    def test_staff_performance_requires_staff_id(self):
        from apps.ai.tools import execute_get_staff_performance

        result = execute_get_staff_performance(user=None)
        assert "error" in result

    def test_staff_performance_not_found(self):
        from apps.ai.tools import execute_get_staff_performance

        result = execute_get_staff_performance(user=None, staff_id=99999)
        assert result["total_bookings"] == 0


@pytest.mark.django_db
class TestAdminToolsWithData:
    def test_revenue_analytics_with_data(self, staff_user):
        from decimal import Decimal

        from apps.ai.tools import execute_get_revenue_analytics

        service = ServiceFactory(price=Decimal("50.00"))
        AppointmentFactory(
            status="completed",
            service=service,
            business=service.business,
        )
        result = execute_get_revenue_analytics(user=None)
        assert result["total_bookings"] == 1

    def test_staff_analytics_with_data(self):
        from apps.ai.tools import execute_get_staff_analytics

        staff = StaffFactory()
        StaffProfileFactory(user=staff)
        AppointmentFactory(
            status="completed",
            staff=staff,
            business=staff.staff_profile.business,
        )
        result = execute_get_staff_analytics(user=staff)
        assert len(result["staff"]) >= 1

    def test_booking_analytics_with_data(self):
        from apps.ai.tools import execute_get_booking_analytics

        AppointmentFactory(status="completed")
        result = execute_get_booking_analytics(user=None)
        assert result["total"] == 1
        assert result["completed"] == 1

    def test_top_services_with_data(self):
        from apps.ai.tools import execute_get_top_services

        service = ServiceFactory()
        AppointmentFactory(status="completed", service=service, business=service.business)
        result = execute_get_top_services(user=None, top_n=3)
        assert len(result["services"]) == 1

    def test_staff_performance_with_data(self):
        from apps.ai.tools import execute_get_staff_performance

        staff = StaffFactory()
        AppointmentFactory(status="completed", staff=staff)
        result = execute_get_staff_performance(user=None, staff_id=staff.id)
        assert result["total_bookings"] == 1


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────


def _next_weekday(weekday):
    today = timezone.now().date()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)
