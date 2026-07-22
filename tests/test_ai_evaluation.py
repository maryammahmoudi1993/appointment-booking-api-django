"""Tests for AI observability and evaluation frameworks."""

from unittest.mock import patch

import pytest

from apps.ai.evaluation import (
    EvalCase,
    EvalResult,
    evaluate_tool_params,
    evaluate_tool_selection,
    run_eval_suite,
    summarize_results,
)
from apps.ai.observability import (
    CopilotInteraction,
    MetricsCollector,
    ToolCallRecord,
    log_tool_call,
    timed,
)

# ────────────────────────────────────────────────────────────────
# Observability
# ────────────────────────────────────────────────────────────────


class TestToolCallRecord:
    def test_creates_record(self):
        rec = ToolCallRecord(
            tool_name="search_services",
            args={"query": "hair"},
            result={"services": []},
            error=None,
            duration_ms=12.5,
        )
        assert rec.tool_name == "search_services"
        assert rec.error is None
        assert rec.duration_ms == 12.5

    def test_error_record(self):
        rec = ToolCallRecord(
            tool_name="boom",
            args={},
            result=None,
            error="division by zero",
            duration_ms=1.0,
        )
        assert rec.error == "division by zero"


class TestCopilotInteraction:
    def test_creates_interaction(self):
        interaction = CopilotInteraction(
            user_id=1,
            message="Hello",
            reply="Hi there",
        )
        assert interaction.user_id == 1
        assert interaction.tool_calls == []
        assert interaction.rounds == 0

    def test_to_dict(self):
        tc = ToolCallRecord(
            tool_name="search_services",
            args={"query": "hair"},
            result={"services": []},
            error=None,
            duration_ms=15.0,
        )
        interaction = CopilotInteraction(
            user_id=1,
            message="Show me services",
            reply="Here are your services",
            tool_calls=[tc],
            total_duration_ms=150.0,
            rounds=1,
        )
        d = interaction.to_dict()
        assert d["user_id"] == 1
        assert len(d["tool_calls"]) == 1
        assert d["tool_calls"][0]["tool"] == "search_services"
        assert d["total_duration_ms"] == 150.0


class TestMetricsCollector:
    def test_empty_metrics(self):
        mc = MetricsCollector()
        m = mc.get_metrics()
        assert m.total_interactions == 0
        assert m.tool_call_success_rate == 0.0

    def test_records_interaction(self):
        mc = MetricsCollector()
        tc = ToolCallRecord(
            tool_name="search_services",
            args={},
            result={},
            error=None,
            duration_ms=10.0,
        )
        interaction = CopilotInteraction(
            user_id=1,
            message="Hi",
            reply="Hello",
            tool_calls=[tc],
            total_duration_ms=100.0,
        )
        mc.record_interaction(interaction)
        m = mc.get_metrics()
        assert m.total_interactions == 1
        assert m.total_tool_calls == 1
        assert m.tool_errors == 0
        assert m.tool_call_success_rate == 100.0
        assert m.tool_frequency["search_services"] == 1

    def test_records_error(self):
        mc = MetricsCollector()
        tc = ToolCallRecord(
            tool_name="boom",
            args={},
            result=None,
            error="error",
            duration_ms=5.0,
        )
        interaction = CopilotInteraction(
            user_id=1,
            message="Hi",
            reply="Error",
            tool_calls=[tc],
            total_duration_ms=50.0,
        )
        mc.record_interaction(interaction)
        m = mc.get_metrics()
        assert m.tool_errors == 1
        assert m.tool_call_success_rate == 0.0

    def test_get_recent_interactions(self):
        mc = MetricsCollector()
        for i in range(5):
            interaction = CopilotInteraction(
                user_id=i,
                message=f"msg{i}",
                reply=f"reply{i}",
            )
            mc.record_interaction(interaction)
        recent = mc.get_recent_interactions(limit=3)
        assert len(recent) == 3
        assert recent[-1]["user_id"] == 4

    def test_reset(self):
        mc = MetricsCollector()
        mc.record_interaction(
            CopilotInteraction(user_id=1, message="Hi", reply="Hello")
        )
        mc.reset()
        m = mc.get_metrics()
        assert m.total_interactions == 0


class TestLogToolCall:
    @patch("apps.ai.observability.logger")
    def test_logs_success(self, mock_logger):
        log_tool_call("search_services", {"query": "hair"}, {"ok": True}, None, 10.0)
        mock_logger.log.assert_called_once()
        args = mock_logger.log.call_args
        assert args[0][0] == 10  # DEBUG level

    @patch("apps.ai.observability.logger")
    def test_logs_error(self, mock_logger):
        log_tool_call("boom", {}, None, "error", 5.0)
        args = mock_logger.log.call_args
        assert args[0][0] == 30  # WARNING level


class TestTimedDecorator:
    def test_measures_time(self):
        @timed
        def slow_func():
            return 42

        result, elapsed = slow_func()
        assert result == 42
        assert elapsed >= 0


# ────────────────────────────────────────────────────────────────
# Evaluation
# ────────────────────────────────────────────────────────────────


class TestEvalCase:
    def test_creates_case(self):
        case = EvalCase(
            name="test",
            message="hello",
            expected_tools=["search_services"],
        )
        assert case.name == "test"
        assert case.tags == []


class TestEvaluateToolSelection:
    def test_exact_match(self):
        assert evaluate_tool_selection("msg", ["a"], ["a"]) is True

    def test_subset_match(self):
        assert evaluate_tool_selection("msg", ["a"], ["a", "b"]) is True

    def test_no_match(self):
        assert evaluate_tool_selection("msg", ["a"], ["b"]) is False

    def test_multiple_expected(self):
        assert evaluate_tool_selection("msg", ["a", "b"], ["a", "b", "c"]) is True

    def test_empty_expected(self):
        assert evaluate_tool_selection("msg", [], ["a"]) is True


class TestEvaluateToolParams:
    def test_no_expected(self):
        assert evaluate_tool_params(None, {"query": "hair"}) is True

    def test_exact_match(self):
        assert evaluate_tool_params({"query": "hair"}, {"query": "hair"}) is True

    def test_partial_match(self):
        assert evaluate_tool_params(
            {"query": "hair"}, {"query": "hair styling"}
        ) is True

    def test_missing_param(self):
        assert evaluate_tool_params({"query": "hair"}, {}) is False

    def test_mismatch(self):
        assert evaluate_tool_params({"query": "hair"}, {"query": "nails"}) is False


class TestRunEvalSuite:
    def test_runs_with_mock_fn(self):
        def mock_eval_fn(message):
            return ["search_services"], {"query": message}

        cases = [
            EvalCase(name="a", message="What services?", expected_tools=["search_services"]),
            EvalCase(name="b", message="Do you have hair styling?", expected_tools=["search_services"]),
        ]
        results = run_eval_suite(mock_eval_fn, cases)
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_captures_errors(self):
        def failing_fn(message):
            raise ValueError("boom")

        case = EvalCase(name="fail", message="test", expected_tools=["x"])
        results = run_eval_suite(failing_fn, [case])
        assert len(results) == 1
        assert results[0].passed is False
        assert "boom" in results[0].error

    def test_tool_selection_failure(self):
        def wrong_tool_fn(message):
            return ["wrong_tool"], {}

        case = EvalCase(
            name="wrong", message="test", expected_tools=["search_services"]
        )
        results = run_eval_suite(wrong_tool_fn, [case])
        assert results[0].passed is False
        assert results[0].tools_correct is False


class TestSummarizeResults:
    def test_summary(self):
        results = [
            EvalResult(
                case_name="a", tools_called=["x"], tools_correct=True,
                params_correct=True, passed=True,
            ),
            EvalResult(
                case_name="b", tools_called=["y"], tools_correct=False,
                params_correct=False, passed=False,
            ),
            EvalResult(
                case_name="c", tools_called=[], tools_correct=False,
                params_correct=False, passed=False, error="boom",
            ),
        ]
        summary = summarize_results(results)
        assert summary["total"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 2
        assert summary["errors"] == 1
        assert summary["pass_rate"] == pytest.approx(33.33, rel=0.01)
        assert len(summary["failures"]) == 2

    def test_empty_summary(self):
        summary = summarize_results([])
        assert summary["total"] == 0
        assert summary["pass_rate"] == 0.0
