"""
Hybrid weighted-scoring service recommender with explainability.

Scoring factors:
  - history_score:   customer's past booking frequency for the service
  - rating_score:    average review rating for the service
  - availability_score: whether staff for this service have near-term openings
  - popularity_score: overall booking volume for the service
  - recency_score:   boost for services booked recently by this customer

Each factor is normalised to [0, 1] and combined using configurable weights.
The engine returns per-service explanations alongside the ranked list.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from django.db.models import Avg, Count
from django.utils import timezone

if TYPE_CHECKING:
    pass


DEFAULT_WEIGHTS: dict[str, float] = {
    "history": 0.30,
    "rating": 0.25,
    "availability": 0.20,
    "popularity": 0.15,
    "recency": 0.10,
}

AVAILABILITY_WINDOW_DAYS = 7


@dataclass
class ServiceScore:
    service_id: int
    service_name: str
    total_score: float
    factors: dict[str, float]
    explanation: str


def _history_scores(customer_id: int, business_id: int | None) -> dict[int, float]:
    """Booking frequency per service for this customer, normalised to [0, 1]."""
    from apps.appointments.models import Appointment
    from apps.services.models import Service

    qs = Appointment.objects.filter(
        customer_id=customer_id,
        status__in=("confirmed", "completed"),
    )
    if business_id:
        qs = qs.filter(business_id=business_id)

    counts = dict(
        qs.values_list("service_id")
        .annotate(cnt=Count("id"))
        .values_list("service_id", "cnt")
    )

    if not counts:
        return {}

    max_count = max(counts.values()) or 1
    all_services = Service.objects.filter(
        business_id=business_id
    ).values_list("id", flat=True) if business_id else Service.objects.all().values_list("id", flat=True)

    return {sid: counts.get(sid, 0) / max_count for sid in all_services}


def _rating_scores(business_id: int | None) -> dict[int, float]:
    """Average review rating per service, normalised to [0, 1]."""
    from apps.engagement.models import Review
    from apps.services.models import Service

    review_qs = Review.objects.all()
    if business_id:
        review_qs = review_qs.filter(business_id=business_id)

    ratings = dict(
        review_qs.values("appointment__service_id")
        .annotate(avg_rating=Avg("rating"))
        .values_list("appointment__service_id", "avg_rating")
    )

    all_services = Service.objects.filter(
        business_id=business_id
    ).values_list("id", flat=True) if business_id else Service.objects.all().values_list("id", flat=True)

    return {sid: (ratings.get(sid, 0) or 0) / 5.0 for sid in all_services}


def _availability_scores(business_id: int | None) -> dict[int, float]:
    """Whether staff offering each service have openings in the next 7 days."""
    from apps.staff.models import StaffProfile

    now = timezone.now()
    window_end = now + timedelta(days=AVAILABILITY_WINDOW_DAYS)

    sp_qs = StaffProfile.objects.all()
    if business_id:
        sp_qs = sp_qs.filter(business_id=business_id)

    service_staff = {}
    for sp in sp_qs.prefetch_related("services_offered"):
        for svc in sp.services_offered.all():
            service_staff.setdefault(svc.id, []).append(sp.user_id)

    result: dict[int, float] = {}
    for service_id in service_staff:
        from apps.staff.services import get_available_slots

        has_slots = False
        for staff_user_id in service_staff[service_id]:
            day = now.date()
            while day <= window_end.date() and not has_slots:
                slots = get_available_slots(
                    staff_user_id=staff_user_id,
                    service_id=service_id,
                    target_date=day,
                )
                if slots:
                    has_slots = True
                day += timedelta(days=1)

        result[service_id] = 1.0 if has_slots else 0.0

    return result


def _popularity_scores(business_id: int | None) -> dict[int, float]:
    """Total booking count per service, normalised to [0, 1]."""
    from apps.appointments.models import Appointment

    qs = Appointment.objects.filter(status__in=("confirmed", "completed"))
    if business_id:
        qs = qs.filter(business_id=business_id)

    counts = dict(
        qs.values("service_id")
        .annotate(cnt=Count("id"))
        .values_list("service_id", "cnt")
    )

    if not counts:
        return {}

    max_count = max(counts.values()) or 1
    from apps.services.models import Service

    all_services = Service.objects.filter(
        business_id=business_id
    ).values_list("id", flat=True) if business_id else Service.objects.all().values_list("id", flat=True)

    return {sid: counts.get(sid, 0) / max_count for sid in all_services}


def _recency_scores(customer_id: int, business_id: int | None) -> dict[int, float]:
    """Recency boost: more recent bookings yield higher scores."""
    from apps.appointments.models import Appointment

    now = timezone.now()
    decay_days = 90.0

    qs = Appointment.objects.filter(
        customer_id=customer_id,
        status__in=("confirmed", "completed"),
    )
    if business_id:
        qs = qs.filter(business_id=business_id)

    last_bookings = {}
    for appt in qs.order_by("-start_datetime"):
        sid = appt.service_id
        if sid not in last_bookings:
            last_bookings[sid] = appt.start_datetime

    result: dict[int, float] = {}
    for sid, dt in last_bookings.items():
        days_ago = (now - dt).total_seconds() / 86400.0
        result[sid] = max(0.0, 1.0 - (days_ago / decay_days))

    return result


def recommend_services(
    customer_id: int | None = None,
    business_id: int | None = None,
    *,
    top_n: int = 5,
    weights: dict[str, float] | None = None,
) -> list[ServiceScore]:
    """
    Return up to *top_n* services ranked by weighted hybrid score.

    When *customer_id* is None (guest user), history/recency scores are
    zero and recommendations are based on popularity, ratings, and
    availability only.
    """
    from apps.services.models import Service

    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    service_qs = Service.objects.filter(is_active=True)
    if business_id:
        service_qs = service_qs.filter(business_id=business_id)

    services = {s.id: s for s in service_qs}
    if not services:
        return []

    list(services.keys())

    history = _history_scores(customer_id, business_id) if customer_id else {}
    ratings = _rating_scores(business_id)
    availability = _availability_scores(business_id)
    popularity = _popularity_scores(business_id)
    recency = _recency_scores(customer_id, business_id) if customer_id else {}

    scores: list[ServiceScore] = []

    for sid, svc in services.items():
        h = history.get(sid, 0.0)
        r = ratings.get(sid, 0.0)
        a = availability.get(sid, 0.0)
        p = popularity.get(sid, 0.0)
        rec = recency.get(sid, 0.0)

        total = (
            w["history"] * h
            + w["rating"] * r
            + w["availability"] * a
            + w["popularity"] * p
            + w["recency"] * rec
        )

        factors = {
            "history": round(h, 3),
            "rating": round(r, 3),
            "availability": round(a, 3),
            "popularity": round(p, 3),
            "recency": round(rec, 3),
        }

        parts = []
        if h > 0:
            parts.append(f"you've booked this {round(h * 100)}% as often as your top service")
        if r > 0:
            parts.append(f"rated {round(r * 5, 1)}/5 by customers")
        if a > 0:
            parts.append("staff have availability within 7 days")
        if p > 0:
            parts.append(f"popular ({round(p * 100)}% of top booking volume)")
        if rec > 0:
            parts.append(f"booked recently ({round(rec * 100)}% recency)")

        explanation = "Recommended because: " + "; ".join(parts) + "." if parts else "No strong signals — ranked by default popularity."

        scores.append(ServiceScore(
            service_id=sid,
            service_name=svc.name,
            total_score=round(total, 4),
            factors=factors,
            explanation=explanation,
        ))

    scores.sort(key=lambda s: s.total_score, reverse=True)
    return scores[:top_n]
