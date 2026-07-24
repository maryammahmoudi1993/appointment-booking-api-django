"""
Revenue forecasting engine using exponential smoothing.

Provides daily/weekly revenue forecasts with confidence intervals
based on historical completed appointment revenue.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ForecastPoint:
    date: str
    predicted_revenue: float
    lower_bound: float
    upper_bound: float


@dataclass
class RevenueForecast:
    granularity: str
    forecast_points: list[ForecastPoint]
    historical_avg_daily: float
    total_forecast: float
    trend: str  # "up", "down", "stable"
    explanation: str


def _aggregate_revenue(business_id: int | None, granularity: str) -> dict[str, float]:
    """Aggregate revenue by time bucket."""
    from apps.appointments.models import Appointment

    qs = Appointment.objects.filter(status="completed")
    if business_id:
        qs = qs.filter(business_id=business_id)

    revenue_map: dict[str, float] = {}

    for appt in qs.select_related("service"):
        dt = appt.start_datetime
        if granularity == "daily":
            key = dt.strftime("%Y-%m-%d")
        elif granularity == "weekly":
            key = dt.strftime("%Y-W%W")
        elif granularity == "monthly":
            key = dt.strftime("%Y-%m")
        else:
            key = dt.strftime("%Y-%m-%d")

        revenue_map[key] = revenue_map.get(key, 0) + float(appt.service.price)

    return revenue_map


def _exponential_smoothing_forecast(
    values: list[float], forecast_steps: int, alpha: float = 0.3
) -> tuple[list[float], list[float], list[float]]:
    """
    Simple exponential smoothing with trend estimation.
    Returns (predictions, lower_bounds, upper_bounds).
    """
    if not values:
        return [0.0] * forecast_steps, [0.0] * forecast_steps, [0.0] * forecast_steps

    n = len(values)
    arr = np.array(values, dtype=np.float64)

    level = arr[0]
    for val in arr:
        level = alpha * val + (1 - alpha) * level

    if n >= 2:
        trend_vals = np.diff(arr)
        trend = float(np.mean(trend_vals[-min(10, n) :]))
    else:
        trend = 0.0

    residuals = arr - (level + trend * np.arange(n))
    std = float(np.std(residuals)) if n > 1 else float(np.mean(np.abs(arr))) * 0.2
    std = max(std, 0.01)

    predictions = []
    lowers = []
    uppers = []

    for i in range(1, forecast_steps + 1):
        pred = level + trend * i
        pred = max(0.0, pred)

        z = 1.96
        lower = max(0.0, pred - z * std * np.sqrt(i))
        upper = pred + z * std * np.sqrt(i)

        predictions.append(round(pred, 2))
        lowers.append(round(lower, 2))
        uppers.append(round(upper, 2))

    return predictions, lowers, uppers


def forecast_revenue(
    business_id: int | None = None,
    *,
    forecast_days: int = 30,
    granularity: str = "daily",
) -> RevenueForecast:
    """
    Forecast future revenue using exponential smoothing on historical data.
    """
    forecast_days = min(max(forecast_days, 7), 365)

    revenue_map = _aggregate_revenue(business_id, granularity)

    if not revenue_map:
        return RevenueForecast(
            granularity=granularity,
            forecast_points=[],
            historical_avg_daily=0.0,
            total_forecast=0.0,
            trend="stable",
            explanation="No historical revenue data available for forecasting.",
        )

    sorted_keys = sorted(revenue_map.keys())
    values = [revenue_map[k] for k in sorted_keys]

    avg_revenue = float(np.mean(values))
    float(np.sum(values))

    step_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(granularity, 1)
    forecast_steps = max(1, forecast_days // step_days)

    predictions, lowers, uppers = _exponential_smoothing_forecast(
        values, forecast_steps
    )

    if len(values) >= 2:
        first_half = float(np.mean(values[: len(values) // 2]))
        second_half = float(np.mean(values[len(values) // 2 :]))
        if second_half > first_half * 1.1:
            trend = "up"
        elif second_half < first_half * 0.9:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    last_date = timezone.now().date()
    points = []
    for i, (pred, lower, upper) in enumerate(zip(predictions, lowers, uppers)):
        if granularity == "daily":
            future_date = last_date + timedelta(days=i + 1)
            date_str = future_date.isoformat()
        elif granularity == "weekly":
            future_date = last_date + timedelta(weeks=i + 1)
            date_str = f"{future_date.isoformat()} (week)"
        else:
            future_month = last_date.month + i + 1
            future_year = last_date.year
            while future_month > 12:
                future_month -= 12
                future_year += 1
            date_str = f"{future_year:04d}-{future_month:02d}"

        points.append(
            ForecastPoint(
                date=date_str,
                predicted_revenue=pred,
                lower_bound=lower,
                upper_bound=upper,
            )
        )

    total_forecast = round(sum(p.predicted_revenue for p in points), 2)

    if trend == "up":
        trend_desc = "Revenue trend is increasing."
    elif trend == "down":
        trend_desc = "Revenue trend is declining."
    else:
        trend_desc = "Revenue is stable."

    explanation = (
        f"Based on {len(values)} historical {granularity} periods with "
        f"avg ${avg_revenue:.2f}/period. "
        f"{trend_desc} "
        f"Forecast for next {forecast_days} days: ${total_forecast:.2f}."
    )

    return RevenueForecast(
        granularity=granularity,
        forecast_points=points,
        historical_avg_daily=round(avg_revenue, 2),
        total_forecast=total_forecast,
        trend=trend,
        explanation=explanation,
    )
