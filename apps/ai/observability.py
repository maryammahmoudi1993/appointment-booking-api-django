"""
AI Observability: structured logging, metrics, and audit trail for all
copilot interactions including tool calls, latency, and token usage.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("apps.ai.observability")


@dataclass
class ToolCallRecord:
    tool_name: str
    args: dict[str, Any]
    result: Any
    error: str | None
    duration_ms: float


@dataclass
class CopilotInteraction:
    user_id: int | None
    message: str
    reply: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    total_duration_ms: float = 0.0
    total_tokens_used: int = 0
    rounds: int = 0
    is_admin: bool = False

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "message": self.message[:200],
            "reply": self.reply[:200],
            "tool_calls": [
                {
                    "tool": tc.tool_name,
                    "args": tc.args,
                    "error": tc.error,
                    "duration_ms": round(tc.duration_ms, 2),
                }
                for tc in self.tool_calls
            ],
            "total_duration_ms": round(self.total_duration_ms, 2),
            "total_tokens_used": self.total_tokens_used,
            "rounds": self.rounds,
            "is_admin": self.is_admin,
        }


@dataclass
class MetricsSnapshot:
    total_interactions: int = 0
    total_tool_calls: int = 0
    tool_errors: int = 0
    avg_duration_ms: float = 0.0
    tool_call_success_rate: float = 0.0
    tool_frequency: dict[str, int] = field(default_factory=dict)


class MetricsCollector:
    """In-memory metrics collector for the copilot.

    In production, swap with a real metrics backend (Prometheus, Datadog, etc.).
    """

    def __init__(self):
        self._interactions: list[CopilotInteraction] = []
        self._tool_calls: list[ToolCallRecord] = []

    def record_interaction(self, interaction: CopilotInteraction):
        self._interactions.append(interaction)
        self._tool_calls.extend(interaction.tool_calls)
        logger.info(
            "copilot_interaction",
            extra={
                "user_id": interaction.user_id,
                "tool_calls_count": len(interaction.tool_calls),
                "duration_ms": interaction.total_duration_ms,
                "is_admin": interaction.is_admin,
            },
        )

    def get_metrics(self) -> MetricsSnapshot:
        total = len(self._interactions)
        tc_count = len(self._tool_calls)
        errors = sum(1 for tc in self._tool_calls if tc.error)

        avg_duration = 0.0
        if total:
            avg_duration = sum(i.total_duration_ms for i in self._interactions) / total

        success_rate = 0.0
        if tc_count:
            success_rate = ((tc_count - errors) / tc_count) * 100

        tool_freq: dict[str, int] = {}
        for tc in self._tool_calls:
            tool_freq[tc.tool_name] = tool_freq.get(tc.tool_name, 0) + 1

        return MetricsSnapshot(
            total_interactions=total,
            total_tool_calls=tc_count,
            tool_errors=errors,
            avg_duration_ms=round(avg_duration, 2),
            tool_call_success_rate=round(success_rate, 2),
            tool_frequency=tool_freq,
        )

    def get_recent_interactions(self, limit: int = 10) -> list[dict]:
        return [i.to_dict() for i in self._interactions[-limit:]]

    def reset(self):
        self._interactions.clear()
        self._tool_calls.clear()


collector = MetricsCollector()


def log_tool_call(
    tool_name: str,
    args: dict,
    result: Any,
    error: str | None,
    duration_ms: float,
):
    """Log a single tool call for observability."""
    level = logging.WARNING if error else logging.DEBUG
    logger.log(
        level,
        "tool_call: %s | error=%s | duration=%.1fms",
        tool_name,
        error or "none",
        duration_ms,
        extra={
            "tool_name": tool_name,
            "args_keys": list(args.keys()),
            "error": error,
            "duration_ms": duration_ms,
        },
    )


def timed(func):
    """Decorator that measures execution time in milliseconds."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = (time.monotonic() - start) * 1000
        return result, elapsed

    return wrapper
