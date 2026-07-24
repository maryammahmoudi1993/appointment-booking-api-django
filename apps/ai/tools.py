"""
Tool registry for AI copilot function calling.

Each tool is a dict with:
  - name: unique identifier matching the Gemini function name
  - description: shown to the LLM
  - parameters: JSON Schema for the function's arguments
  - execute: callable(**kwargs) -> dict | str  (returns data the LLM can use)

The LLM never touches Django models directly — it only sees the data
these functions return.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone


def _get_business(user):
    """Resolve the business for the current user."""
    from apps.business.models import BusinessMembership

    if user and user.is_authenticated:
        membership = BusinessMembership.objects.filter(user=user).first()
        if membership:
            return membership.business
    from apps.business.models import Business

    return Business.objects.filter(is_active=True).first()


def _serialize_service(s):
    return {
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "duration_minutes": s.duration_minutes,
        "price": str(s.price),
        "category": s.category,
    }


def _serialize_staff(sp):
    return {
        "id": sp.user_id,
        "name": sp.user.get_full_name() or sp.user.username,
        "services": list(sp.services_offered.values_list("name", flat=True)),
    }


# ────────────────────────────────────────────────────────────────────
# Informational tools (read-only)
# ────────────────────────────────────────────────────────────────────


def execute_search_services(**kwargs):
    from apps.services.models import Service

    business = _get_business(kwargs.get("user"))
    qs = Service.objects.filter(is_active=True)
    if business:
        qs = qs.filter(business=business)
    query = kwargs.get("query", "")
    if query:
        qs = qs.filter(name__icontains=query)
    category = kwargs.get("category")
    if category:
        qs = qs.filter(category__icontains=category)
    return {"services": [_serialize_service(s) for s in qs[:10]]}


def execute_get_service_details(**kwargs):
    from apps.services.models import Service

    service_id = kwargs.get("service_id")
    if not service_id:
        return {"error": "service_id is required."}
    try:
        s = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return {"error": f"Service {service_id} not found."}
    return _serialize_service(s)


def execute_get_staff(**kwargs):
    from apps.staff.models import StaffProfile

    business = _get_business(kwargs.get("user"))
    qs = StaffProfile.objects.select_related("user").all()
    if business:
        qs = qs.filter(business=business)
    service_name = kwargs.get("service_name")
    if service_name:
        qs = qs.filter(services_offered__name__icontains=service_name)
    return {"staff": [_serialize_staff(sp) for sp in qs[:20]]}


def execute_suggest_staff(**kwargs):
    from apps.staff.models import StaffProfile

    service_id = kwargs.get("service_id")
    if not service_id:
        return {"error": "service_id is required."}
    business = _get_business(kwargs.get("user"))
    qs = StaffProfile.objects.select_related("user").filter(
        services_offered__id=service_id
    )
    if business:
        qs = qs.filter(business=business)
    return {"staff": [_serialize_staff(sp) for sp in qs[:10]]}


def execute_find_available_slots(**kwargs):
    from apps.staff.models import StaffProfile
    from apps.staff.services import get_available_slots

    service_id = kwargs.get("service_id")
    target = kwargs.get("date")
    staff_id = kwargs.get("staff_id")

    if not service_id or not target:
        return {"error": "service_id and date are required."}

    if isinstance(target, str):
        try:
            target = date.fromisoformat(target)
        except ValueError:
            return {"error": f"Invalid date format: {target}. Use YYYY-MM-DD."}

    from apps.services.models import Service

    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return {"error": f"Service {service_id} not found."}

    staff_ids = []
    if staff_id:
        staff_ids = [staff_id]
    else:
        staff_ids = list(
            StaffProfile.objects.filter(services_offered__id=service_id).values_list(
                "user_id", flat=True
            )
        )

    results = []
    for sid in staff_ids:
        sp = StaffProfile.objects.filter(user_id=sid).first()
        business = sp.business if sp else None
        bs = getattr(business, "settings", None) if business else None
        slots = get_available_slots(sid, target, bs)
        available = [s for s in slots if s["available"]]
        staff_name = ""
        if sp:
            staff_name = sp.user.get_full_name() or sp.user.username
        results.append(
            {
                "staff_id": sid,
                "staff_name": staff_name,
                "date": target.isoformat(),
                "available_slots": [
                    {
                        "start": s["start"].strftime("%H:%M"),
                        "end": s["end"].strftime("%H:%M"),
                    }
                    for s in available
                ],
                "total_available": len(available),
            }
        )
    return {"results": results, "service": _serialize_service(service)}


def execute_get_appointments(**kwargs):
    from apps.appointments.models import Appointment

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required to view appointments."}

    qs = Appointment.objects.filter(
        customer=user, status__in=["pending", "confirmed"]
    ).select_related("staff", "service")

    status_filter = kwargs.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    results = []
    for a in qs[:20]:
        results.append(
            {
                "id": a.id,
                "service": a.service.name,
                "staff": a.staff.get_full_name() or a.staff.username,
                "start": a.start_datetime.isoformat(),
                "end": a.end_datetime.isoformat(),
                "status": a.status,
            }
        )
    return {"appointments": results}


def execute_get_business_info(**kwargs):
    business = _get_business(kwargs.get("user"))
    if not business:
        return {"error": "No business information available."}
    return {
        "name": business.name,
        "type": business.get_business_type_display(),
        "phone": business.phone,
        "email": business.email,
        "address": business.address,
        "timezone": business.timezone,
        "currency": business.currency,
    }


# ────────────────────────────────────────────────────────────────────
# Side-effecting tools (create drafts, confirm, cancel)
# ────────────────────────────────────────────────────────────────────


DRAFT_EXPIRY_MINUTES = 15


def execute_create_booking_draft(**kwargs):
    from apps.ai.models import BookingDraft, Conversation
    from apps.services.models import Service
    from apps.staff.models import StaffProfile

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required to create a booking draft."}

    service_id = kwargs.get("service_id")
    staff_id = kwargs.get("staff_id")
    date_str = kwargs.get("date")
    start_time = kwargs.get("start_time")

    if not all([service_id, staff_id, date_str, start_time]):
        return {"error": "service_id, staff_id, date, and start_time are required."}

    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return {"error": f"Service {service_id} not found."}

    if not StaffProfile.objects.filter(user_id=staff_id).exists():
        return {"error": f"Staff {staff_id} not found."}

    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return {"error": f"Invalid date format: {date_str}. Use YYYY-MM-DD."}

    parts = start_time.split(":")
    hour, minute = int(parts[0]), int(parts[1])
    start_dt = timezone.make_aware(
        timezone.datetime.combine(
            target_date, timezone.datetime.min.time().replace(hour=hour, minute=minute)
        )
    )
    end_dt = start_dt + timedelta(minutes=service.duration_minutes)

    business = _get_business(user)

    conversation_id = kwargs.get("conversation_id")
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            pass

    draft = BookingDraft.objects.create(
        conversation=conversation,
        user=user,
        business=business,
        service=service,
        staff_id=staff_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        price=service.price,
        expires_at=timezone.now() + timedelta(minutes=DRAFT_EXPIRY_MINUTES),
    )

    staff_sp = (
        StaffProfile.objects.filter(user_id=staff_id).select_related("user").first()
    )
    staff_name = (
        staff_sp.user.get_full_name() or staff_sp.user.username
        if staff_sp
        else "Unknown"
    )

    return {
        "draft_id": str(draft.id),
        "service": service.name,
        "staff": staff_name,
        "staff_id": staff_id,
        "date": target_date.isoformat(),
        "start_time": start_time,
        "end_time": end_dt.strftime("%H:%M"),
        "price": str(service.price),
        "expires_in_minutes": DRAFT_EXPIRY_MINUTES,
        "message": (
            f"Booking proposal created. Please confirm: "
            f"{service.name} with {staff_name} on {target_date.isoformat()} "
            f"at {start_time}-{end_dt.strftime('%H:%M')} for ${service.price}. "
            f"This proposal expires in {DRAFT_EXPIRY_MINUTES} minutes."
        ),
    }


def execute_get_booking_draft(**kwargs):
    from apps.ai.models import BookingDraft

    draft_id = kwargs.get("draft_id")
    if not draft_id:
        return {"error": "draft_id is required."}

    try:
        draft = BookingDraft.objects.select_related("service", "staff", "user").get(
            id=draft_id
        )
    except BookingDraft.DoesNotExist:
        return {"error": "Draft not found."}

    if draft.is_expired() and draft.status == "pending":
        draft.status = "expired"
        draft.save(update_fields=["status"])

    staff_name = draft.staff.get_full_name() or draft.staff.username

    return {
        "draft_id": str(draft.id),
        "service": draft.service.name,
        "staff": staff_name,
        "staff_id": draft.staff_id,
        "date": draft.start_datetime.date().isoformat(),
        "start_time": draft.start_datetime.strftime("%H:%M"),
        "end_time": draft.end_datetime.strftime("%H:%M"),
        "price": str(draft.price),
        "status": draft.status,
        "is_expired": draft.is_expired(),
    }


def execute_confirm_booking_draft(**kwargs):
    from apps.ai.models import BookingDraft

    draft_id = kwargs.get("draft_id")
    if not draft_id:
        return {"error": "draft_id is required."}

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required."}

    try:
        draft = BookingDraft.objects.select_related("service", "staff").get(
            id=draft_id, user=user
        )
    except BookingDraft.DoesNotExist:
        return {"error": "Draft not found."}

    if draft.is_expired():
        draft.status = "expired"
        draft.save(update_fields=["status"])
        return {"error": "This booking draft has expired. Please start a new booking."}

    if draft.status != "pending":
        return {"error": f"Draft is already {draft.status}."}

    appointment, error = draft.confirm()
    if error:
        return {"error": error}

    staff_name = draft.staff.get_full_name() or draft.staff.username
    return {
        "success": True,
        "appointment_id": appointment.id,
        "service": draft.service.name,
        "staff": staff_name,
        "date": appointment.start_datetime.date().isoformat(),
        "start_time": appointment.start_datetime.strftime("%H:%M"),
        "end_time": appointment.end_datetime.strftime("%H:%M"),
        "status": appointment.status,
        "message": (
            f"Booking confirmed! Your appointment #{appointment.id}: "
            f"{draft.service.name} with {staff_name} on "
            f"{appointment.start_datetime.date().isoformat()} at "
            f"{appointment.start_datetime.strftime('%H:%M')}."
        ),
    }


def execute_create_reschedule_draft(**kwargs):
    from apps.ai.models import BookingDraft, Conversation
    from apps.appointments.models import Appointment

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required."}

    appointment_id = kwargs.get("appointment_id")
    new_date = kwargs.get("new_date")
    new_start_time = kwargs.get("new_start_time")

    if not all([appointment_id, new_date, new_start_time]):
        return {"error": "appointment_id, new_date, and new_start_time are required."}

    try:
        appt = Appointment.objects.select_related("service", "staff").get(
            id=appointment_id, customer=user, status__in=["pending", "confirmed"]
        )
    except Appointment.DoesNotExist:
        return {"error": "Appointment not found or not reschedulable."}

    try:
        target_date = date.fromisoformat(new_date)
    except ValueError:
        return {"error": f"Invalid date: {new_date}. Use YYYY-MM-DD."}

    parts = new_start_time.split(":")
    hour, minute = int(parts[0]), int(parts[1])
    new_start = timezone.make_aware(
        timezone.datetime.combine(
            target_date, timezone.datetime.min.time().replace(hour=hour, minute=minute)
        )
    )
    new_end = new_start + timedelta(minutes=appt.service.duration_minutes)

    conversation_id = kwargs.get("conversation_id")
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            pass

    draft = BookingDraft.objects.create(
        conversation=conversation,
        user=user,
        business=appt.business,
        service=appt.service,
        staff=appt.staff,
        start_datetime=new_start,
        end_datetime=new_end,
        price=appt.service.price,
        expires_at=timezone.now() + timedelta(minutes=DRAFT_EXPIRY_MINUTES),
        notes=f"Reschedule of appointment #{appointment_id}",
    )

    staff_name = appt.staff.get_full_name() or appt.staff.username
    return {
        "draft_id": str(draft.id),
        "original_appointment_id": appointment_id,
        "service": appt.service.name,
        "staff": staff_name,
        "new_date": new_date,
        "new_start_time": new_start_time,
        "new_end_time": new_end.strftime("%H:%M"),
        "message": (
            f"Reschedule proposal: {appt.service.name} with {staff_name} moved to "
            f"{new_date} at {new_start_time}-{new_end.strftime('%H:%M')}. "
            f"Please confirm to reschedule."
        ),
    }


def execute_confirm_reschedule(**kwargs):
    from apps.ai.models import BookingDraft
    from apps.appointments.validators import update_appointment_atomic

    draft_id = kwargs.get("draft_id")
    if not draft_id:
        return {"error": "draft_id is required."}

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required."}

    try:
        draft = BookingDraft.objects.get(id=draft_id, user=user)
    except BookingDraft.DoesNotExist:
        return {"error": "Draft not found."}

    if draft.is_expired():
        draft.status = "expired"
        draft.save(update_fields=["status"])
        return {"error": "Reschedule draft has expired."}

    if draft.status != "pending":
        return {"error": f"Draft is already {draft.status}."}

    original_id = int(draft.notes.split("#")[-1]) if "#" in draft.notes else None
    if not original_id:
        return {"error": "Cannot determine original appointment."}

    try:
        appointment = update_appointment_atomic(
            appointment_id=original_id,
            staff_id=draft.staff_id,
            service_id=draft.service_id,
            start_datetime=draft.start_datetime,
            end_datetime=draft.end_datetime,
            changed_by=user,
        )
    except Exception as e:
        return {"error": f"Reschedule failed: {e}"}

    draft.status = "confirmed"
    draft.confirmed_at = timezone.now()
    draft.appointment = appointment
    draft.save(update_fields=["status", "confirmed_at", "appointment_id"])

    appointment.staff.get_full_name() or appointment.staff.username
    return {
        "success": True,
        "appointment_id": appointment.id,
        "message": (
            f"Appointment #{appointment.id} rescheduled to "
            f"{appointment.start_datetime.date().isoformat()} at "
            f"{appointment.start_datetime.strftime('%H:%M')}."
        ),
    }


def execute_create_cancellation_draft(**kwargs):
    from apps.ai.models import BookingDraft, Conversation
    from apps.appointments.models import Appointment

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required."}

    appointment_id = kwargs.get("appointment_id")
    if not appointment_id:
        return {"error": "appointment_id is required."}

    try:
        appt = Appointment.objects.select_related("service", "staff").get(
            id=appointment_id, customer=user, status__in=["pending", "confirmed"]
        )
    except Appointment.DoesNotExist:
        return {"error": "Appointment not found or not cancellable."}

    conversation_id = kwargs.get("conversation_id")
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            pass

    draft = BookingDraft.objects.create(
        conversation=conversation,
        user=user,
        business=appt.business,
        service=appt.service,
        staff=appt.staff,
        start_datetime=appt.start_datetime,
        end_datetime=appt.end_datetime,
        price=Decimal("0"),
        expires_at=timezone.now() + timedelta(minutes=DRAFT_EXPIRY_MINUTES),
        notes=f"Cancel appointment #{appointment_id}",
    )

    staff_name = appt.staff.get_full_name() or appt.staff.username
    return {
        "draft_id": str(draft.id),
        "appointment_id": appointment_id,
        "service": appt.service.name,
        "staff": staff_name,
        "date": appt.start_datetime.date().isoformat(),
        "start_time": appt.start_datetime.strftime("%H:%M"),
        "message": (
            f"Cancel appointment #{appointment_id}: {appt.service.name} with "
            f"{staff_name} on {appt.start_datetime.date().isoformat()} at "
            f"{appt.start_datetime.strftime('%H:%M')}? Please confirm."
        ),
    }


def execute_confirm_cancellation(**kwargs):
    from apps.ai.models import BookingDraft
    from apps.appointments.models import Appointment

    draft_id = kwargs.get("draft_id")
    if not draft_id:
        return {"error": "draft_id is required."}

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required."}

    try:
        draft = BookingDraft.objects.get(id=draft_id, user=user)
    except BookingDraft.DoesNotExist:
        return {"error": "Draft not found."}

    if draft.is_expired():
        draft.status = "expired"
        draft.save(update_fields=["status"])
        return {"error": "Cancellation draft has expired."}

    if draft.status != "pending":
        return {"error": f"Draft is already {draft.status}."}

    original_id = int(draft.notes.split("#")[-1]) if "#" in draft.notes else None
    if not original_id:
        return {"error": "Cannot determine original appointment."}

    try:
        appt = Appointment.objects.get(
            id=original_id, customer=user, status__in=["pending", "confirmed"]
        )
    except Appointment.DoesNotExist:
        return {"error": "Appointment not found."}

    appt._changed_by = user
    appt.status = "cancelled"
    appt.save(update_fields=["status", "updated_at"])

    draft.status = "confirmed"
    draft.confirmed_at = timezone.now()
    draft.save(update_fields=["status", "confirmed_at"])

    return {
        "success": True,
        "appointment_id": appt.id,
        "message": f"Appointment #{appt.id} has been cancelled.",
    }


# ────────────────────────────────────────────────────────────────────
# No-show Prediction
# ────────────────────────────────────────────────────────────────────


def execute_predict_no_show(user, **kwargs):
    """Predict no-show risk for a specific appointment."""
    from apps.ai.no_show import predict_no_show

    appointment_id = kwargs.get("appointment_id")
    if not appointment_id:
        return {"error": "appointment_id is required."}

    try:
        from apps.appointments.models import Appointment

        appt = Appointment.objects.select_related("customer", "staff", "service").get(
            id=appointment_id
        )
    except Appointment.DoesNotExist:
        return {"error": f"Appointment #{appointment_id} not found."}

    result = predict_no_show(appt)

    return {
        "appointment_id": appt.id,
        "customer": appt.customer.get_full_name() or appt.customer.username,
        "service": appt.service.name,
        "staff": appt.staff.get_full_name() or appt.staff.username,
        "appointment_time": appt.start_datetime.isoformat(),
        "probability_no_show": result.probability_no_show,
        "risk_level": result.risk_level,
        "feature_contributions": result.feature_contributions,
        "explanation": result.explanation,
    }


# ────────────────────────────────────────────────────────────────────
# Revenue Forecast
# ────────────────────────────────────────────────────────────────────


def execute_forecast_revenue(user, **kwargs):
    """Forecast future revenue using exponential smoothing."""
    from apps.ai.revenue_forecast import forecast_revenue

    business = _get_business(user)
    forecast_days = min(int(kwargs.get("forecast_days", 30)), 365)
    granularity = kwargs.get("granularity", "daily")
    if granularity not in ("daily", "weekly", "monthly"):
        granularity = "daily"

    result = forecast_revenue(
        business_id=business.id if business else None,
        forecast_days=forecast_days,
        granularity=granularity,
    )

    return {
        "granularity": result.granularity,
        "forecast_points": [
            {
                "date": p.date,
                "predicted_revenue": p.predicted_revenue,
                "lower_bound": p.lower_bound,
                "upper_bound": p.upper_bound,
            }
            for p in result.forecast_points
        ],
        "historical_avg_daily": result.historical_avg_daily,
        "total_forecast": result.total_forecast,
        "trend": result.trend,
        "explanation": result.explanation,
    }


# ────────────────────────────────────────────────────────────────────
# Admin Analytics Tools
# ────────────────────────────────────────────────────────────────────


def execute_get_revenue_analytics(user, **kwargs):
    """Get revenue analytics: total revenue, average ticket, monthly breakdown."""
    from decimal import Decimal

    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth

    from apps.appointments.models import Appointment

    business = _get_business(user)
    qs = Appointment.objects.filter(status="completed")
    if business:
        qs = qs.filter(business=business)

    qs = qs.select_related("service")

    total_revenue = qs.aggregate(total=Sum("service__price"))["total"] or Decimal(
        "0.00"
    )
    total_bookings = qs.count()
    average_ticket = (
        total_revenue / total_bookings if total_bookings else Decimal("0.00")
    )

    monthly = (
        qs.annotate(period=TruncMonth("start_datetime"))
        .values("period")
        .annotate(revenue=Sum("service__price"), bookings=Count("id"))
        .order_by("period")
    )

    return {
        "total_revenue": str(total_revenue),
        "total_bookings": total_bookings,
        "average_ticket": str(round(average_ticket, 2)),
        "revenue_by_period": [
            {
                "period": p["period"].strftime("%Y-%m") if p["period"] else "unknown",
                "revenue": str(p["revenue"]),
                "bookings": p["bookings"],
            }
            for p in monthly
        ],
    }


def execute_get_staff_analytics(user, **kwargs):
    """Get staff analytics: booking counts, revenue, and ratings per staff member."""
    from decimal import Decimal

    from django.db.models import Avg, Count, Q, Sum

    from apps.appointments.models import Appointment
    from apps.engagement.models import Review
    from apps.staff.models import StaffProfile

    business = _get_business(user)
    qs = Appointment.objects.all()
    if business:
        qs = qs.filter(business=business)

    staff_ids = (
        StaffProfile.objects.filter(business=business).values_list("user_id", flat=True)
        if business
        else StaffProfile.objects.all().values_list("user_id", flat=True)
    )

    staff_data = (
        qs.filter(staff_id__in=staff_ids)
        .values("staff_id", "staff__first_name", "staff__last_name", "staff__username")
        .annotate(
            total_bookings=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
            revenue=Sum("service__price", filter=Q(status="completed")),
        )
        .order_by("-total_bookings")
    )

    review_map = {}
    if business:
        for r in (
            Review.objects.filter(staff_id__in=list(staff_ids), business=business)
            .values("staff_id")
            .annotate(avg_rating=Avg("rating"), count=Count("id"))
        ):
            review_map[r["staff_id"]] = r

    return {
        "staff": [
            {
                "staff_id": s["staff_id"],
                "name": f"{s['staff__first_name']} {s['staff__last_name']}".strip()
                or s["staff__username"],
                "total_bookings": s["total_bookings"],
                "completed": s["completed"],
                "revenue": str(s["revenue"] or Decimal("0.00")),
                "average_rating": round(
                    review_map.get(s["staff_id"], {}).get("avg_rating", 0) or 0, 2
                ),
                "review_count": review_map.get(s["staff_id"], {}).get("count", 0),
            }
            for s in staff_data
        ]
    }


def execute_get_service_analytics(user, **kwargs):
    """Get service analytics: booking counts, revenue, ratings per service."""
    from decimal import Decimal

    from django.db.models import Avg, Count, Q, Sum

    from apps.appointments.models import Appointment
    from apps.engagement.models import Review

    business = _get_business(user)
    qs = Appointment.objects.all()
    if business:
        qs = qs.filter(business=business)

    service_data = (
        qs.values("service_id", "service__name", "service__duration_minutes")
        .annotate(
            total_bookings=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
            revenue=Sum("service__price", filter=Q(status="completed")),
        )
        .order_by("-total_bookings")
    )

    service_ids = [s["service_id"] for s in service_data]
    review_map = {}
    if business:
        for r in (
            Review.objects.filter(
                appointment__service_id__in=service_ids, business=business
            )
            .values("appointment__service_id")
            .annotate(avg_rating=Avg("rating"), count=Count("id"))
        ):
            review_map[r["appointment__service_id"]] = r

    return {
        "services": [
            {
                "service_id": s["service_id"],
                "name": s["service__name"],
                "total_bookings": s["total_bookings"],
                "completed": s["completed"],
                "revenue": str(s["revenue"] or Decimal("0.00")),
                "average_rating": round(
                    review_map.get(s["service_id"], {}).get("avg_rating", 0) or 0, 2
                ),
                "duration_minutes": s["service__duration_minutes"],
            }
            for s in service_data
        ]
    }


def execute_get_booking_analytics(user, **kwargs):
    """Get aggregate booking stats: totals, completion/cancellation rates."""
    from django.db.models import Count

    from apps.appointments.models import Appointment

    business = _get_business(user)
    qs = Appointment.objects.all()
    if business:
        qs = qs.filter(business=business)

    total = qs.count()
    status_counts = dict(
        qs.values_list("status").annotate(c=Count("id")).values_list("status", "c")
    )
    completed = status_counts.get("completed", 0)
    cancelled = status_counts.get("cancelled", 0)
    completion_rate = round((completed / total * 100) if total else 0, 2)
    cancellation_rate = round((cancelled / total * 100) if total else 0, 2)

    return {
        "total": total,
        "pending": status_counts.get("pending", 0),
        "confirmed": status_counts.get("confirmed", 0),
        "cancelled": cancelled,
        "completed": completed,
        "completion_rate": completion_rate,
        "cancellation_rate": cancellation_rate,
    }


def execute_get_top_services(user, **kwargs):
    """Get top services ranked by booking count or revenue."""
    from django.db.models import Count, Sum

    from apps.appointments.models import Appointment

    business = _get_business(user)
    qs = Appointment.objects.filter(status="completed")
    if business:
        qs = qs.filter(business=business)

    top_n = min(int(kwargs.get("top_n", 5)), 20)
    rank_by = kwargs.get("rank_by", "bookings")
    if rank_by not in ("bookings", "revenue"):
        rank_by = "bookings"

    order = "-total_bookings" if rank_by == "bookings" else "-total_revenue"

    services = (
        qs.values("service_id", "service__name")
        .annotate(
            total_bookings=Count("id"),
            total_revenue=Sum("service__price"),
        )
        .order_by(order)[:top_n]
    )

    return {
        "services": [
            {
                "service_id": s["service_id"],
                "name": s["service__name"],
                "total_bookings": s["total_bookings"],
                "total_revenue": str(s["total_revenue"] or Decimal("0.00")),
            }
            for s in services
        ]
    }


def execute_get_staff_performance(user, **kwargs):
    """Get detailed performance comparison for a specific staff member."""
    from decimal import Decimal

    from django.db.models import Avg, Count, Sum

    from apps.appointments.models import Appointment
    from apps.engagement.models import Review

    staff_id = kwargs.get("staff_id")
    if not staff_id:
        return {"error": "staff_id is required."}

    business = _get_business(user)
    qs = Appointment.objects.filter(staff_id=staff_id)
    if business:
        qs = qs.filter(business=business)

    total = qs.count()
    completed = qs.filter(status="completed").count()
    cancelled = qs.filter(status="cancelled").count()
    revenue = qs.filter(status="completed").aggregate(total=Sum("service__price"))[
        "total"
    ] or Decimal("0.00")

    review_qs = Review.objects.filter(staff_id=staff_id)
    if business:
        review_qs = review_qs.filter(business=business)

    review_stats = review_qs.aggregate(avg_rating=Avg("rating"), count=Count("id"))

    service_breakdown = (
        qs.filter(status="completed")
        .values("service__name")
        .annotate(count=Count("id"), rev=Sum("service__price"))
        .order_by("-count")
    )

    return {
        "staff_id": staff_id,
        "total_bookings": total,
        "completed": completed,
        "cancelled": cancelled,
        "completion_rate": round((completed / total * 100) if total else 0, 2),
        "total_revenue": str(revenue),
        "average_rating": round(review_stats.get("avg_rating", 0) or 0, 2),
        "review_count": review_stats.get("count", 0),
        "top_services": [
            {
                "name": s["service__name"],
                "bookings": s["count"],
                "revenue": str(s["rev"] or Decimal("0.00")),
            }
            for s in service_breakdown[:5]
        ],
    }


# ────────────────────────────────────────────────────────────────────
# Recommendations
# ────────────────────────────────────────────────────────────────────


def execute_recommend_services(user, **kwargs):
    """Recommend services to a customer using hybrid weighted scoring."""
    from apps.ai.recommender import recommend_services

    business = _get_business(user)
    top_n = min(int(kwargs.get("top_n", 5)), 20)
    customer_id = user.id if user and user.is_authenticated else None

    results = recommend_services(
        customer_id=customer_id,
        business_id=business.id if business else None,
        top_n=top_n,
    )

    return {
        "recommendations": [
            {
                "service_id": r.service_id,
                "service_name": r.service_name,
                "score": r.total_score,
                "factors": r.factors,
                "explanation": r.explanation,
            }
            for r in results
        ],
        "count": len(results),
    }


# ────────────────────────────────────────────────────────────────────
# Registry
# ────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "search_services",
        "description": "Search for services by name or category. Returns matching services with details.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term for service name.",
                },
                "category": {
                    "type": "string",
                    "description": "Filter by service category.",
                },
            },
            "required": [],
        },
        "execute": execute_search_services,
    },
    {
        "name": "get_service_details",
        "description": "Get full details for a specific service by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_id": {"type": "integer", "description": "The service ID."},
            },
            "required": ["service_id"],
        },
        "execute": execute_get_service_details,
    },
    {
        "name": "get_staff",
        "description": "List staff members. Optionally filter by service name.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Filter staff who offer this service.",
                },
            },
            "required": [],
        },
        "execute": execute_get_staff,
    },
    {
        "name": "suggest_staff",
        "description": "Suggest staff members who offer a specific service. Use service_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_id": {
                    "type": "integer",
                    "description": "The service ID to find staff for.",
                },
            },
            "required": ["service_id"],
        },
        "execute": execute_suggest_staff,
    },
    {
        "name": "find_available_slots",
        "description": (
            "Find available time slots for a service on a given date. "
            "Optionally filter by staff_id. Returns structured slot data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "service_id": {"type": "integer", "description": "The service ID."},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format."},
                "staff_id": {
                    "type": "integer",
                    "description": "Optional: specific staff member ID.",
                },
            },
            "required": ["service_id", "date"],
        },
        "execute": execute_find_available_slots,
    },
    {
        "name": "get_appointments",
        "description": "Get the current customer's upcoming appointments.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "confirmed", "cancelled", "completed"],
                    "description": "Optional filter by status.",
                },
            },
            "required": [],
        },
        "execute": execute_get_appointments,
    },
    {
        "name": "get_business_info",
        "description": "Get business information: name, type, phone, email, timezone.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "execute": execute_get_business_info,
    },
    {
        "name": "create_booking_draft",
        "description": (
            "Create a booking proposal (draft). This does NOT create an appointment. "
            "The user must explicitly confirm before the booking is finalized."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "service_id": {"type": "integer", "description": "The service ID."},
                "staff_id": {
                    "type": "integer",
                    "description": "The staff member's user ID.",
                },
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format."},
                "start_time": {
                    "type": "string",
                    "description": "Start time in HH:MM format.",
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional conversation UUID.",
                },
            },
            "required": ["service_id", "staff_id", "date", "start_time"],
        },
        "execute": execute_create_booking_draft,
    },
    {
        "name": "get_booking_draft",
        "description": "Check the status and details of an existing booking draft.",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {"type": "string", "description": "The draft UUID."},
            },
            "required": ["draft_id"],
        },
        "execute": execute_get_booking_draft,
    },
    {
        "name": "confirm_booking_draft",
        "description": (
            "Confirm a booking draft to create the actual appointment. "
            "This is the ONLY way to create an appointment through the AI."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "The draft UUID to confirm.",
                },
            },
            "required": ["draft_id"],
        },
        "execute": execute_confirm_booking_draft,
    },
    {
        "name": "create_reschedule_draft",
        "description": "Propose rescheduling an existing appointment to a new date/time.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The appointment to reschedule.",
                },
                "new_date": {
                    "type": "string",
                    "description": "New date in YYYY-MM-DD format.",
                },
                "new_start_time": {
                    "type": "string",
                    "description": "New start time in HH:MM format.",
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional conversation UUID.",
                },
            },
            "required": ["appointment_id", "new_date", "new_start_time"],
        },
        "execute": execute_create_reschedule_draft,
    },
    {
        "name": "confirm_reschedule",
        "description": "Confirm a reschedule draft to finalize the reschedule.",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "The reschedule draft UUID.",
                },
            },
            "required": ["draft_id"],
        },
        "execute": execute_confirm_reschedule,
    },
    {
        "name": "create_cancellation_draft",
        "description": "Propose cancelling an existing appointment. Requires confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The appointment to cancel.",
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional conversation UUID.",
                },
            },
            "required": ["appointment_id"],
        },
        "execute": execute_create_cancellation_draft,
    },
    {
        "name": "confirm_cancellation",
        "description": "Confirm a cancellation draft to finalize the cancellation.",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "The cancellation draft UUID.",
                },
            },
            "required": ["draft_id"],
        },
        "execute": execute_confirm_cancellation,
    },
    {
        "name": "recommend_services",
        "description": (
            "Recommend services to a customer based on their booking history, "
            "reviews, availability, and popularity. Returns ranked services "
            "with explanations for each recommendation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "description": "Number of recommendations to return (default 5).",
                },
            },
            "required": [],
        },
        "execute": execute_recommend_services,
    },
    {
        "name": "predict_no_show",
        "description": (
            "Predict whether a customer is likely to no-show for a specific appointment. "
            "Returns a risk level, probability, and explainable factor contributions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The appointment ID to predict no-show risk for.",
                },
            },
            "required": ["appointment_id"],
        },
        "execute": execute_predict_no_show,
    },
    {
        "name": "forecast_revenue",
        "description": (
            "Forecast future revenue based on historical completed appointment data. "
            "Returns daily/weekly/monthly predictions with confidence intervals."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "forecast_days": {
                    "type": "integer",
                    "description": "Number of days to forecast (default 30, max 365).",
                },
                "granularity": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly"],
                    "description": "Forecast granularity (default daily).",
                },
            },
            "required": [],
        },
        "execute": execute_forecast_revenue,
    },
    {
        "name": "get_revenue_analytics",
        "description": (
            "Get revenue analytics including total revenue, average ticket size, "
            "and monthly breakdown. Admin-only tool for business analytics."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "execute": execute_get_revenue_analytics,
    },
    {
        "name": "get_staff_analytics",
        "description": (
            "Get staff analytics including booking counts, revenue per staff, "
            "and average ratings. Admin-only tool for staff performance tracking."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "execute": execute_get_staff_analytics,
    },
    {
        "name": "get_service_analytics",
        "description": (
            "Get service analytics including booking counts, revenue per service, "
            "and average ratings. Admin-only tool for service performance tracking."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "execute": execute_get_service_analytics,
    },
    {
        "name": "get_booking_analytics",
        "description": (
            "Get aggregate booking statistics including totals, completion rates, "
            "and cancellation rates. Admin-only tool for booking overview."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "execute": execute_get_booking_analytics,
    },
    {
        "name": "get_top_services",
        "description": (
            "Get top services ranked by booking count or revenue. "
            "Admin-only tool for identifying most popular or profitable services."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "description": "Number of services to return (default 5, max 20).",
                },
                "rank_by": {
                    "type": "string",
                    "enum": ["bookings", "revenue"],
                    "description": "Rank by bookings or revenue (default bookings).",
                },
            },
            "required": [],
        },
        "execute": execute_get_top_services,
    },
    {
        "name": "get_staff_performance",
        "description": (
            "Get detailed performance for a specific staff member including "
            "bookings, revenue, ratings, and top services."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "staff_id": {
                    "type": "integer",
                    "description": "The staff member's user ID.",
                },
            },
            "required": ["staff_id"],
        },
        "execute": execute_get_staff_performance,
    },
]

TOOL_MAP = {t["name"]: t for t in TOOL_DEFINITIONS}


def get_tool_declarations():
    """Return raw tool definitions (name/description/parameters) for the
    admin copilot's tool allowlist filtering. Provider-specific formatting
    (e.g. Gemini's Tool/FunctionDeclaration objects) happens in
    gemini_client.build_tool()."""
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        }
        for t in TOOL_DEFINITIONS
    ]


def execute_tool(tool_name, user, **kwargs):
    """Execute a registered tool by name. Returns (result_dict, error_string|None)."""
    if tool_name not in TOOL_MAP:
        return None, f"Unknown tool: {tool_name}"
    try:
        result = TOOL_MAP[tool_name]["execute"](user=user, **kwargs)
        return result, None
    except Exception as e:
        return None, f"Tool execution error: {e}"
