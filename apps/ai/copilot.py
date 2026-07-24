"""
BloomFlow AI Copilot — OpenAI function-calling service.

The copilot receives a user message, optionally calls tools, and returns
a final text response.  The LLM never accesses Django models directly;
it only sees data returned by the allowlisted tools in tools.py.
"""

import json
import logging
from dataclasses import dataclass, field

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
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
    "AI copilot is not configured. Please set the OPENAI_API_KEY "
    "environment variable to enable the AI assistant."
)

FALLBACK_PROVIDER_ERROR = (
    "Sorry, I'm having trouble reaching the AI assistant right now. "
    "Please try again in a moment."
)


@dataclass
class CopilotResponse:
    reply: str
    tool_calls_made: list = field(default_factory=list)
    conversation_id: str | None = None


def _get_client():
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        return None
    try:
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    except ImportError:
        logger.warning("openai package not installed")
        return None


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


def chat(
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

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation:
        history = _load_history(conversation)
        messages.extend(history)
    elif conversation_history:
        messages.extend(conversation_history)

    if not any(m["role"] == "user" and m["content"] == user_message for m in messages):
        messages.append({"role": "user", "content": user_message})

    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": " ".join(t["description"].split()),
                "parameters": t["parameters"],
            },
        }
        for t in TOOL_DEFINITIONS
    ]

    tool_calls_made = []

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = client.chat.completions.create(
                model=MODEL, messages=messages, tools=openai_tools, tool_choice="auto"
            )
        except Exception:
            # An invalid/rejected API key, rate limit, or transient network
            # error should degrade to a friendly message, not an uncaught
            # 500 — the AI provider is an external dependency the rest of
            # the request pipeline shouldn't crash over.
            logger.exception("OpenAI request failed in copilot.chat()")
            return CopilotResponse(
                reply=FALLBACK_PROVIDER_ERROR,
                tool_calls_made=tool_calls_made,
                conversation_id=str(conversation.id) if conversation else None,
            )

        choice = response.choices[0]
        msg = choice.message

        if not msg.tool_calls:
            reply = msg.content or ""
            if conversation:
                _save_message(conversation, "assistant", reply)
            return CopilotResponse(
                reply=reply,
                tool_calls_made=tool_calls_made,
                conversation_id=str(conversation.id) if conversation else None,
            )

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            if conversation:
                args["conversation_id"] = str(conversation.id)

            tool_calls_made.append({"tool": tool_name, "args": args})
            result, error = execute_tool(tool_name, user=user, **args)

            if error:
                result = {"error": error}

            result_str = json.dumps(result)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result_str}
            )

            if conversation:
                _save_message(
                    conversation,
                    "tool",
                    result_str[:500],
                    tool_name=tool_name,
                    tool_call_id=tc.id,
                )

    final = messages[-1]
    reply = final.get("content", "I'm sorry, I couldn't complete your request.")
    if conversation:
        _save_message(conversation, "assistant", reply)
    return CopilotResponse(
        reply=reply,
        tool_calls_made=tool_calls_made,
        conversation_id=str(conversation.id) if conversation else None,
    )
