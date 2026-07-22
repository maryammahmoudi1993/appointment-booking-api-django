"""
AI Evaluation framework: tests that verify tool selection accuracy,
parameter correctness, and overall copilot quality.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("apps.ai.evaluation")


@dataclass
class EvalCase:
    name: str
    message: str
    expected_tools: list[str]
    expected_params: dict[str, Any] | None = None
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    case_name: str
    tools_called: list[str]
    tools_correct: bool
    params_correct: bool
    passed: bool
    error: str | None = None


# ────────────────────────────────────────────────────────────────
# Standard evaluation dataset
# ────────────────────────────────────────────────────────────────

EVAL_DATASET: list[EvalCase] = [
    EvalCase(
        name="search_services",
        message="What services do you offer?",
        expected_tools=["search_services"],
        tags=["informational"],
    ),
    EvalCase(
        name="search_services_with_query",
        message="Do you have hair styling available?",
        expected_tools=["search_services"],
        expected_params={"query": "hair styling"},
        tags=["informational"],
    ),
    EvalCase(
        name="get_service_details",
        message="Tell me more about the manicure service",
        expected_tools=["get_service_details"],
        tags=["informational"],
    ),
    EvalCase(
        name="get_staff",
        message="Who are your staff members?",
        expected_tools=["get_staff"],
        tags=["informational"],
    ),
    EvalCase(
        name="find_available_slots",
        message="What times are available for a haircut tomorrow?",
        expected_tools=["find_available_slots"],
        tags=["scheduling"],
    ),
    EvalCase(
        name="business_hours",
        message="What are your opening hours?",
        expected_tools=["get_business_info"],
        tags=["informational"],
    ),
    EvalCase(
        name="get_appointments",
        message="Show me my upcoming appointments",
        expected_tools=["get_appointments"],
        tags=["informational"],
    ),
    EvalCase(
        name="revenue_query",
        message="How much revenue did we make last month?",
        expected_tools=["get_revenue_analytics"],
        tags=["admin", "analytics"],
    ),
    EvalCase(
        name="staff_performance_query",
        message="How is Sarah performing this month?",
        expected_tools=["get_staff_analytics"],
        tags=["admin", "analytics"],
    ),
    EvalCase(
        name="booking_stats",
        message="What is our completion rate?",
        expected_tools=["get_booking_analytics"],
        tags=["admin", "analytics"],
    ),
    EvalCase(
        name="top_services_query",
        message="What are our most popular services?",
        expected_tools=["get_top_services"],
        tags=["admin", "analytics"],
    ),
]


# ────────────────────────────────────────────────────────────────
# Evaluation runner
# ────────────────────────────────────────────────────────────────


def evaluate_tool_selection(
    message: str,
    expected_tools: list[str],
    tool_calls: list[str],
) -> bool:
    """Check if the correct tools were called (order-insensitive)."""
    return set(expected_tools).issubset(set(tool_calls))


def evaluate_tool_params(
    expected_params: dict[str, Any] | None,
    actual_args: dict[str, Any],
) -> bool:
    """Check if the expected params were present in the actual args."""
    if not expected_params:
        return True
    for key, value in expected_params.items():
        if key not in actual_args:
            return False
        actual = str(actual_args[key]).lower()
        expected = str(value).lower()
        if expected not in actual and actual not in expected:
            return False
    return True


def run_eval_suite(
    eval_fn: Callable[[str], tuple[list[str], dict]],
    cases: list[EvalCase] | None = None,
) -> list[EvalResult]:
    """
    Run evaluation cases through the provided eval function.

    eval_fn should accept a message and return (tool_names_called, tool_args_map).
    """
    if cases is None:
        cases = EVAL_DATASET

    results = []
    for case in cases:
        try:
            tool_names, tool_args = eval_fn(case.message)
            tools_ok = evaluate_tool_selection(case.message, case.expected_tools, tool_names)
            params_ok = evaluate_tool_params(case.expected_params, tool_args)
            results.append(
                EvalResult(
                    case_name=case.name,
                    tools_called=tool_names,
                    tools_correct=tools_ok,
                    params_correct=params_ok,
                    passed=tools_ok and params_ok,
                )
            )
        except Exception as e:
            results.append(
                EvalResult(
                    case_name=case.name,
                    tools_called=[],
                    tools_correct=False,
                    params_correct=False,
                    passed=False,
                    error=str(e),
                )
            )

    return results


def summarize_results(results: list[EvalResult]) -> dict:
    """Summarize evaluation results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    errors = sum(1 for r in results if r.error)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round((passed / total * 100) if total else 0, 2),
        "failures": [
            {"case": r.case_name, "error": r.error, "tools_called": r.tools_called}
            for r in results
            if not r.passed
        ],
    }
