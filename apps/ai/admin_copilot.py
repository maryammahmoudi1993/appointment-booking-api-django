"""
Admin copilot service for business managers.

Uses the same tool-calling pattern as the customer copilot but with
admin-specific analytics tools. Only accessible to admin-role users.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

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


@dataclass
class AdminCopilotResponse:
    reply: str
    tool_calls_made: list[str] = field(default_factory=list)


def admin_chat(message: str, user=None, conversation_id=None) -> AdminCopilotResponse:
    """
    Process an admin analytics query using tool-calling.

    ``user`` must be the authenticated requesting admin so that every
    analytics tool resolves to *their* business via BusinessMembership.
    Without it, tool resolution silently falls back to "the first active
    business in the database," leaking other businesses' data.
    """
    import openai
    from django.conf import settings

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        return AdminCopilotResponse(
            reply="AI analytics copilot requires an OpenAI API key. "
            "Please configure OPENAI_API_KEY in your environment."
        )

    client = openai.OpenAI(api_key=api_key)

    from apps.ai.tools import get_openai_tools

    admin_tool_names = {
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

    all_tools = get_openai_tools()
    admin_tools = [t for t in all_tools if t["function"]["name"] in admin_tool_names]

    messages = [
        {"role": "system", "content": ADMIN_SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    tool_calls_made = []
    max_rounds = 5

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=admin_tools or None,
        )

        choice = response.choices[0]
        assistant_msg = choice.message

        if not assistant_msg.tool_calls:
            return AdminCopilotResponse(
                reply=assistant_msg.content or "I couldn't generate a response.",
                tool_calls_made=tool_calls_made,
            )

        messages.append(assistant_msg)

        from apps.ai.tools import execute_tool

        for tc in assistant_msg.tool_calls:
            fn_name = tc.function.name
            import json

            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            tool_calls_made.append(fn_name)

            result, error = execute_tool(fn_name, user=user, **args)

            if error:
                result = {"error": error}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result) if result else "No data available.",
            })

    return AdminCopilotResponse(
        reply="I've reached the maximum number of tool calls. "
        "Please try a simpler question.",
        tool_calls_made=tool_calls_made,
    )
