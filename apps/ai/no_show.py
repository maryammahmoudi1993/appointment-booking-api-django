"""
No-show prediction engine using XGBoost with SHAP explainability.

Features:
  - Lead time (days between booking and appointment)
  - Hour of day / day of week / weekend flag
  - Customer historical no-show rate and total bookings
  - Staff appointment count (experience proxy)
  - Service popularity (booking volume)

The model is trained on synthetic data seeded from existing appointments.
For a portfolio demo, it trains on-demand from the current database state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from django.utils import timezone

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

FEATURE_NAMES = [
    "lead_time_days",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "customer_total_bookings",
    "customer_no_show_rate",
    "staff_experience",
    "service_popularity",
]


@dataclass
class PredictionResult:
    probability_no_show: float
    risk_level: str  # "low", "medium", "high"
    feature_contributions: dict[str, float]
    explanation: str


def _build_feature_row(appointment) -> list[float]:
    """Extract a feature vector from an existing appointment object."""
    start = appointment.start_datetime
    now = timezone.now()

    lead_time = max(0, (start - now).total_seconds() / 86400.0)
    hour = start.hour
    dow = start.weekday()
    is_weekend = 1.0 if dow >= 5 else 0.0

    from apps.appointments.models import Appointment

    customer_appts = Appointment.objects.filter(
        customer_id=appointment.customer_id
    )
    total = customer_appts.count()

    customer_appts.filter(status="completed").count()
    no_shows = customer_appts.filter(status="cancelled").count()
    no_show_rate = no_shows / total if total > 0 else 0.0

    staff_exp = Appointment.objects.filter(
        staff_id=appointment.staff_id
    ).exclude(id=appointment.id).count()

    svc_pop = Appointment.objects.filter(
        service_id=appointment.service_id
    ).exclude(id=appointment.id).count()

    return [
        lead_time,
        hour,
        dow,
        is_weekend,
        total,
        no_show_rate,
        staff_exp,
        svc_pop,
    ]


def _build_training_data():
    """
    Generate training data from existing appointments.
    Uses status as proxy: cancelled appointments treated as no-shows,
    completed/confirmed as showed-up.
    """
    from apps.appointments.models import Appointment

    appointments = Appointment.objects.exclude(status="pending").select_related(
        "customer", "staff", "service"
    )

    rows = []
    labels = []

    for appt in appointments:
        row = _build_feature_row(appt)
        rows.append(row)
        labels.append(1 if appt.status == "cancelled" else 0)

    return np.array(rows, dtype=np.float32), np.array(labels, dtype=np.float32)


def _generate_synthetic_training_data(n_samples: int = 1000) -> tuple:
    """
    Generate synthetic training data for initial model training
    when insufficient real data exists.
    """
    rng = np.random.default_rng(42)

    lead_time = rng.exponential(scale=7.0, size=n_samples)
    hour = rng.choice(range(8, 20), size=n_samples)
    dow = rng.integers(0, 7, size=n_samples)
    is_weekend = (dow >= 5).astype(np.float32)
    total_bookings = rng.poisson(lam=5, size=n_samples).astype(np.float32)
    no_show_rate = rng.beta(2, 10, size=n_samples)
    staff_experience = rng.poisson(lam=20, size=n_samples).astype(np.float32)
    service_pop = rng.poisson(lam=15, size=n_samples).astype(np.float32)

    x_data = np.column_stack([
        lead_time, hour, dow, is_weekend,
        total_bookings, no_show_rate, staff_experience, service_pop,
    ]).astype(np.float32)

    logit = (
        0.05 * lead_time
        - 0.02 * hour
        + 0.1 * is_weekend
        + 0.03 * total_bookings
        + 0.8 * no_show_rate
        - 0.01 * staff_experience
        - 0.005 * service_pop
        + rng.normal(0, 0.3, size=n_samples)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    y = (rng.random(n_samples) < prob).astype(np.float32)

    return x_data, y


def _get_model():
    """Load or train the XGBoost model."""
    import xgboost as xgb

    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42,
    )

    real_x, real_y = _build_training_data()

    if len(real_x) < 30:
        logger.info("Insufficient real data (%d samples); using synthetic training data.", len(real_x))
        x_data, y = _generate_synthetic_training_data()
        if len(real_x) > 0:
            x_data = np.vstack([x_data, real_x])
            y = np.concatenate([y, real_y])
    else:
        x_data, y = real_x, real_y

    model.fit(x_data, y)
    return model, x_data


def _compute_shap_values(model, x_data, feature_row) -> dict[str, float]:
    """Compute SHAP values for a single prediction."""
    import shap

    explainer = shap.TreeExplainer(model)
    row = np.array([feature_row], dtype=np.float32)
    shap_values = explainer.shap_values(row)

    if isinstance(shap_values, list):
        vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
    else:
        vals = shap_values[0]

    return {name: round(float(vals[i]), 4) for i, name in enumerate(FEATURE_NAMES)}


def predict_no_show(appointment) -> PredictionResult:
    """
    Predict the no-show probability for an upcoming appointment.
    Returns probability, risk level, SHAP feature contributions, and explanation.
    """
    model, x_data = _get_model()
    feature_row = _build_feature_row(appointment)
    row = np.array([feature_row], dtype=np.float32).reshape(1, -1)

    proba = model.predict_proba(row)[0]
    prob_no_show = float(proba[1])

    if prob_no_show >= 0.6:
        risk_level = "high"
    elif prob_no_show >= 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"

    contributions = _compute_shap_values(model, x_data, feature_row)

    top_factors = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    increasing = [name for name, val in top_factors if val > 0]
    decreasing = [name for name, val in top_factors if val < 0]

    parts = []
    if increasing:
        parts.append("increased by " + ", ".join(increasing))
    if decreasing:
        parts.append("decreased by " + ", ".join(decreasing))

    explanation = (
        f"No-show risk: {risk_level} ({prob_no_show:.0%}). "
        + ("Key factors " + "; ".join(parts) + "." if parts else "No strong signal factors.")
    )

    return PredictionResult(
        probability_no_show=round(prob_no_show, 4),
        risk_level=risk_level,
        feature_contributions=contributions,
        explanation=explanation,
    )
