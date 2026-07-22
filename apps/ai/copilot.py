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
MAX_TOOL_ROUNDS = 5
SYSTEM_PROMPT = (
    "You are BloomFlow, a friendly AI assistant for a booking business. "
    "Help customers with inquiries about services, staff, availability, "
    "and their appointments. Be concise and helpful. "
    "Never create, reschedule, or cancel appointments without explicit "
    "user confirmation. If you need to book an appointment, ask the user "
    "to confirm all details first."
)

FALLBACK_NO_KEY = (
    "AI copilot is not configured. Please set the OPENAI_API_KEY "
    "environment variable to enable the AI assistant."
)


@dataclass
class CopilotResponse:
    reply: str
    tool_calls_made: list = field(default_factory=list)


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


def chat(user_message: str, user=None, conversation_history=None) -> CopilotResponse:
    """
    Process a user message through the copilot.

    Args:
        user_message: The user's text input.
        user: The authenticated Django User (passed to tool executes).
        conversation_history: Optional list of prior messages for multi-turn.

    Returns:
        CopilotResponse with the assistant's final text reply.
    """
    client = _get_client()
    if client is None:
        return CopilotResponse(reply=FALLBACK_NO_KEY)

    from .tools import TOOL_DEFINITIONS, execute_tool

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        }
        for t in TOOL_DEFINITIONS
    ]

    tool_calls_made = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=openai_tools, tool_choice="auto"
        )

        choice = response.choices[0]
        msg = choice.message

        if not msg.tool_calls:
            return CopilotResponse(
                reply=msg.content or "", tool_calls_made=tool_calls_made
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

            tool_calls_made.append({"tool": tool_name, "args": args})
            result, error = execute_tool(tool_name, user=user, **args)

            if error:
                result = {"error": error}

            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)}
            )

    final = messages[-1]
    return CopilotResponse(
        reply=final.get("content", "I'm sorry, I couldn't complete your request."),
        tool_calls_made=tool_calls_made,
    )
