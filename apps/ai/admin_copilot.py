"""
Admin copilot service for business managers.

Uses the same tool-calling pattern as the customer copilot but with
admin-specific analytics tools. Only accessible to admin-role users.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from .gemini_client import MODEL, build_tool, provider_error_reply
from .gemini_client import get_client as _get_client
from .observability import CopilotInteraction, ToolCallRecord, collector

logger = logging.getLogger(__name__)

ADMIN_SYSTEM_PROMPT = """You are BloomFlow Analytics Copilot, an AI assistant for business managers.

You have access to analytics tools that provide insights into:
- Revenue performance
- Staff productivity and ratings
- Service popularity and profitability
- Booking trends and patterns

Always respond in a professional, data-driven tone. Use specific numbers
when available. If data is insufficient to answer a question, say so
honestly. Never fabricate analytics data.

When presenting complex data, summarize key takeaways first, then
provide details if requested."""

ADMIN_TOOL_NAMES = {
    "get_revenue_analytics",
    "get_staff_analytics",
    "get_service_analytics",
    "get_booking_analytics",
    "get_top_services",
    "get_staff_performance",
    "get_business_info",
    "recommend_services",
    "forecast_revenue",
}


@dataclass
class AdminCopilotResponse:
    reply: str
    tool_calls_made: list[str] = field(default_factory=list)


def _admin_chat_impl(
    message: str, user=None, conversation_id=None
) -> AdminCopilotResponse:
    """
    Process an admin analytics query using tool-calling.

    ``user`` must be the authenticated requesting admin so that every
    analytics tool resolves to *their* business via BusinessMembership.
    Without it, tool resolution silently falls back to "the first active
    business in the database," leaking other businesses' data.
    """
    client = _get_client()
    if client is None:
        return AdminCopilotResponse(
            reply="AI analytics copilot requires a Gemini API key. "
            "Please configure GEMINI_API_KEY in your environment."
        )

    from google.genai import types

    from apps.ai.tools import execute_tool, get_tool_declarations

    all_tools = get_tool_declarations()
    admin_tool_defs = [t for t in all_tools if t["name"] in ADMIN_TOOL_NAMES]
    tool = build_tool(admin_tool_defs)

    config = types.GenerateContentConfig(
        system_instruction=ADMIN_SYSTEM_PROMPT,
        tools=[tool],
    )
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=message)])]

    tool_calls_made = []
    max_rounds = 5

    for _ in range(max_rounds):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=contents, config=config
            )
        except Exception as exc:
            logger.exception("Gemini request failed in admin_copilot.admin_chat()")
            return AdminCopilotResponse(
                reply=provider_error_reply(exc),
                tool_calls_made=tool_calls_made,
            )

        candidate = response.candidates[0]
        parts = candidate.content.parts or []
        function_call_parts = [p for p in parts if getattr(p, "function_call", None)]

        if not function_call_parts:
            return AdminCopilotResponse(
                reply=response.text or "I couldn't generate a response.",
                tool_calls_made=tool_calls_made,
            )

        contents.append(candidate.content)

        response_parts = []
        for part in function_call_parts:
            fc = part.function_call
            fn_name = fc.name
            args = dict(fc.args) if fc.args else {}

            tool_calls_made.append(fn_name)

            result, error = execute_tool(fn_name, user=user, **args)

            if error:
                result = {"error": error}

            response_parts.append(
                types.Part.from_function_response(
                    name=fn_name,
                    response=result if result else {"detail": "No data available."},
                )
            )

        contents.append(types.Content(role="user", parts=response_parts))

    return AdminCopilotResponse(
        reply="I've reached the maximum number of tool calls. "
        "Please try a simpler question.",
        tool_calls_made=tool_calls_made,
    )


def admin_chat(message: str, user=None, conversation_id=None) -> AdminCopilotResponse:
    """Run the analytics copilot and record privacy-limited operational metrics."""
    started = time.monotonic()
    response = _admin_chat_impl(
        message=message,
        user=user,
        conversation_id=conversation_id,
    )
    records = [
        ToolCallRecord(
            tool_name=tool_name,
            args={},
            result=None,
            error=None,
            duration_ms=0,
        )
        for tool_name in response.tool_calls_made
    ]
    collector.record_interaction(
        CopilotInteraction(
            user_id=getattr(user, "id", None),
            message="[redacted]",
            reply="[redacted]",
            tool_calls=records,
            total_duration_ms=(time.monotonic() - started) * 1000,
            rounds=len(records),
            is_admin=True,
        )
    )
    return response
