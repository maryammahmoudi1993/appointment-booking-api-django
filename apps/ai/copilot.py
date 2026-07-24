"""
BloomFlow AI Copilot — Gemini function-calling service.

The copilot receives a user message, optionally calls tools, and returns
a final text response.  The LLM never accesses Django models directly;
it only sees data returned by the allowlisted tools in tools.py.
"""

import logging
import time
from dataclasses import dataclass, field

from .gemini_client import MODEL, build_tool, provider_error_reply
from .gemini_client import get_client as _get_client
from .observability import CopilotInteraction, ToolCallRecord, collector

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 8

SYSTEM_PROMPT = """You are BloomFlow, a friendly AI assistant for a booking business called Bloom Studio.

CAPABILITIES:
- Search services and staff
- Find available time slots
- Create booking proposals (drafts)
- Confirm bookings after user approval
- Reschedule existing appointments
- Cancel appointments
- View customer appointments
- Answer business inquiries

CRITICAL RULES:
1. NEVER create, reschedule, or cancel an appointment directly.
2. ALWAYS create a draft first, show the user the details, and ask for explicit confirmation.
3. ONLY after the user confirms, call the confirm tool.
4. If a draft expires, inform the user and offer to create a new one.
5. Never invent services, staff members, or availability. Only use data from tools.
6. Never claim a booking was created without a successful confirm tool call.

BOOKING WORKFLOW:
1. Understand what service the customer wants.
2. Find available slots using find_available_slots.
3. Present options to the customer.
4. When they choose, create a booking draft with create_booking_draft.
5. Show the draft details and ask "Please confirm this booking."
6. Only after they say yes, call confirm_booking_draft.
7. Report the confirmed appointment details.

LANGUAGE:
- Respond in the language the customer uses.
- Support both English and Persian (Farsi).
- Be warm, professional, and concise.
"""

FALLBACK_NO_KEY = (
    "AI copilot is not configured. Please set the GEMINI_API_KEY "
    "environment variable to enable the AI assistant."
)


@dataclass
class CopilotResponse:
    reply: str
    tool_calls_made: list = field(default_factory=list)
    conversation_id: str | None = None


def _save_message(conversation, role, content, tool_name="", tool_call_id=""):
    from .models import Message

    Message.objects.create(
        conversation=conversation,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_call_id=tool_call_id,
    )


def _load_history(conversation, max_messages=20):
    messages = list(conversation.messages.order_by("-created_at")[:max_messages])
    messages.reverse()
    history = []
    for m in messages:
        if m.role in ("user", "assistant") and m.content:
            history.append({"role": m.role, "content": m.content})
    return history


def _gemini_contents(history, user_message):
    """Build a Gemini `contents` list from our internal (user/assistant)
    history plus the new user message. Gemini only has "user"/"model"
    roles — our stored "assistant" role maps to "model" here."""
    from google.genai import types

    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in history
    ]
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    )
    return contents


def _chat_impl(
    user_message: str,
    user=None,
    conversation_id=None,
    conversation_history=None,
) -> CopilotResponse:
    """
    Process a user message through the copilot.

    Args:
        user_message: The user's text input.
        user: The authenticated Django User.
        conversation_id: Optional UUID of an existing conversation.
        conversation_history: Optional list of prior messages (in-memory fallback).

    Returns:
        CopilotResponse with the assistant's final text reply.
    """
    client = _get_client()
    if client is None:
        return CopilotResponse(reply=FALLBACK_NO_KEY)

    from google.genai import types

    from .models import Conversation
    from .tools import TOOL_DEFINITIONS, execute_tool

    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (Conversation.DoesNotExist, Exception):
            pass

    if conversation is None and user and user.is_authenticated:
        business = None
        try:
            from apps.business.models import BusinessMembership

            membership = BusinessMembership.objects.filter(user=user).first()
            if membership:
                business = membership.business
        except Exception:
            pass
        conversation = Conversation.objects.create(user=user, business=business)

    if conversation:
        _save_message(conversation, "user", user_message)

    if conversation:
        history = _load_history(conversation)
    else:
        history = conversation_history or []

    contents = _gemini_contents(history, user_message)

    tool = build_tool(TOOL_DEFINITIONS)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tool],
    )

    tool_calls_made = []

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=contents, config=config
            )
        except Exception as exc:
            # An invalid/rejected API key, rate limit, or transient network
            # error should degrade to a friendly message, not an uncaught
            # 500 — the AI provider is an external dependency the rest of
            # the request pipeline shouldn't crash over.
            logger.exception("Gemini request failed in copilot.chat()")
            return CopilotResponse(
                reply=provider_error_reply(exc),
                tool_calls_made=tool_calls_made,
                conversation_id=str(conversation.id) if conversation else None,
            )

        candidate = response.candidates[0]
        parts = candidate.content.parts or []
        function_call_parts = [p for p in parts if getattr(p, "function_call", None)]

        if not function_call_parts:
            reply = response.text or ""
            if conversation:
                _save_message(conversation, "assistant", reply)
            return CopilotResponse(
                reply=reply,
                tool_calls_made=tool_calls_made,
                conversation_id=str(conversation.id) if conversation else None,
            )

        contents.append(candidate.content)

        response_parts = []
        for part in function_call_parts:
            fc = part.function_call
            tool_name = fc.name
            args = dict(fc.args) if fc.args else {}

            if conversation:
                args["conversation_id"] = str(conversation.id)

            tool_calls_made.append({"tool": tool_name, "args": args})
            result, error = execute_tool(tool_name, user=user, **args)

            if error:
                result = {"error": error}

            response_parts.append(
                types.Part.from_function_response(name=tool_name, response=result)
            )

            if conversation:
                import json

                _save_message(
                    conversation,
                    "tool",
                    json.dumps(result)[:500],
                    tool_name=tool_name,
                )

        contents.append(types.Content(role="user", parts=response_parts))

    reply = "I'm sorry, I couldn't complete your request."
    if conversation:
        _save_message(conversation, "assistant", reply)
    return CopilotResponse(
        reply=reply,
        tool_calls_made=tool_calls_made,
        conversation_id=str(conversation.id) if conversation else None,
    )


def chat(
    user_message: str,
    user=None,
    conversation_id=None,
    conversation_history=None,
) -> CopilotResponse:
    """Run the customer copilot and record privacy-limited operational metrics."""
    started = time.monotonic()
    response = _chat_impl(
        user_message=user_message,
        user=user,
        conversation_id=conversation_id,
        conversation_history=conversation_history,
    )
    records = [
        ToolCallRecord(
            tool_name=call["tool"],
            args={"keys": sorted(call.get("args", {}).keys())},
            result=None,
            error=None,
            duration_ms=0,
        )
        for call in response.tool_calls_made
    ]
    collector.record_interaction(
        CopilotInteraction(
            user_id=getattr(user, "id", None),
            message="[redacted]",
            reply="[redacted]",
            tool_calls=records,
            total_duration_ms=(time.monotonic() - started) * 1000,
            rounds=len(records),
        )
    )
    return response
