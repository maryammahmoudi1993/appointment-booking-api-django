from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Appointment
from apps.business.models import BusinessMembership
from apps.engagement.models import Review
from apps.services.models import Service
from apps.staff.models import StaffProfile
from core.permissions import IsAdminRole


from core.business import get_default_business


def _get_business(user):
    membership = (
        BusinessMembership.objects.filter(user=user)
        .select_related("business")
        .first()
    )
    if membership:
        return membership.business
    return get_default_business()


def _business_appointments(user):
    business = _get_business(user)
    return Appointment.objects.filter(business=business), business


@extend_schema_view(get=extend_schema(
    tags=["Analytics"],
    summary="Revenue analytics",
    description="Admin only. Monthly revenue breakdown, total revenue, average ticket size.",
))
class RevenueAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs, _ = _business_appointments(request.user)
        completed = qs.filter(status="completed").select_related("service")
        total_revenue = completed.aggregate(total=Sum("service__price"))["total"] or Decimal("0.00")
        total_bookings = completed.count()
        average_ticket = total_revenue / total_bookings if total_bookings else Decimal("0.00")

        revenue_by_period = (
            completed
            .annotate(period=TruncMonth("start_datetime"))
            .values("period")
            .annotate(
                revenue=Sum("service__price"),
                bookings=Count("id"),
            )
            .order_by("period")
        )

        revenue_data = [
            {
                "period": p["period"].strftime("%Y-%m") if p["period"] else "unknown",
                "revenue": p["revenue"],
                "bookings": p["bookings"],
            }
            for p in revenue_by_period
        ]

        return Response({
            "total_revenue": str(total_revenue),
            "total_bookings": total_bookings,
            "average_ticket": str(average_ticket),
            "revenue_by_period": revenue_data,
        })


@extend_schema_view(get=extend_schema(
    tags=["Analytics"],
    summary="Staff analytics",
    description="Admin only. Per-staff booking counts, revenue, and average ratings.",
))
class StaffAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs, _ = _business_appointments(request.user)
        staff_ids = StaffProfile.objects.filter(
            business=_get_business(request.user)
        ).values_list("user_id", flat=True)

        staff_appointments = (
            qs.filter(staff_id__in=staff_ids)
            .values("staff_id", "staff__first_name", "staff__last_name", "staff__username")
            .annotate(
                total_bookings=Count("id"),
                completed_bookings=Count("id", filter=Q(status="completed")),
                total_revenue=Sum("service__price", filter=Q(status="completed")),
            )
            .order_by("-total_bookings")
        )

        staff_ids_list = list(staff_ids)
        review_stats = (
            Review.objects.filter(
                staff_id__in=staff_ids_list,
                business=_get_business(request.user),
            )
            .values("staff_id")
            .annotate(
                average_rating=Avg("rating"),
                review_count=Count("id"),
            )
        )
        review_map = {r["staff_id"]: r for r in review_stats}

        result = []
        for s in staff_appointments:
            sid = s["staff_id"]
            name = f"{s['staff__first_name']} {s['staff__last_name']}".strip() or s["staff__username"]
            rv = review_map.get(sid, {})
            result.append({
                "staff_id": sid,
                "staff_name": name,
                "total_bookings": s["total_bookings"],
                "completed_bookings": s["completed_bookings"],
                "total_revenue": str(s["total_revenue"] or Decimal("0.00")),
                "average_rating": round(rv.get("average_rating", 0) or 0, 2),
                "review_count": rv.get("review_count", 0),
            })

        return Response(result)


@extend_schema_view(get=extend_schema(
    tags=["Analytics"],
    summary="Service analytics",
    description="Admin only. Per-service booking counts, revenue, ratings, and average duration.",
))
class ServiceAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs, _ = _business_appointments(request.user)
        business = _get_business(request.user)

        service_stats = (
            qs.values("service_id", "service__name", "service__duration_minutes")
            .annotate(
                total_bookings=Count("id"),
                completed_bookings=Count("id", filter=Q(status="completed")),
                total_revenue=Sum("service__price", filter=Q(status="completed")),
            )
            .order_by("-total_bookings")
        )

        service_ids = [s["service_id"] for s in service_stats]
        review_stats = (
            Review.objects.filter(
                appointment__service_id__in=service_ids,
                business=business,
            )
            .values("appointment__service_id")
            .annotate(
                average_rating=Avg("rating"),
                review_count=Count("id"),
            )
        )
        review_map = {r["appointment__service_id"]: r for r in review_stats}

        result = []
        for s in service_stats:
            sid = s["service_id"]
            rv = review_map.get(sid, {})
            result.append({
                "service_id": sid,
                "service_name": s["service__name"],
                "total_bookings": s["total_bookings"],
                "completed_bookings": s["completed_bookings"],
                "total_revenue": str(s["total_revenue"] or Decimal("0.00")),
                "average_rating": round(rv.get("average_rating", 0) or 0, 2),
                "review_count": rv.get("review_count", 0),
                "average_duration": s["service__duration_minutes"],
            })

        return Response(result)


@extend_schema_view(get=extend_schema(
    tags=["Analytics"],
    summary="Booking analytics",
    description="Admin only. Aggregate booking stats: totals, completion/cancellation rates, average daily bookings.",
))
class BookingAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs, _ = _business_appointments(request.user)
        total = qs.count()
        status_counts = dict(
            qs.values_list("status").annotate(c=Count("id")).values_list("status", "c")
        )
        completed = status_counts.get("completed", 0)
        cancelled = status_counts.get("cancelled", 0)
        completion_rate = (completed / total * 100) if total else 0
        cancellation_rate = (cancelled / total * 100) if total else 0

        total_revenue = (
            qs.filter(status="completed")
            .aggregate(total=Sum("service__price"))["total"]
            or Decimal("0.00")
        )

        first_booking = qs.order_by("start_datetime").values_list("start_datetime", flat=True).first()
        if first_booking:
            days_span = max((timezone.now().date() - first_booking.date()).days, 1)
            avg_daily = total / days_span
        else:
            avg_daily = 0

        return Response({
            "total": total,
            "pending": status_counts.get("pending", 0),
            "confirmed": status_counts.get("confirmed", 0),
            "cancelled": cancelled,
            "completed": completed,
            "completion_rate": round(completion_rate, 2),
            "cancellation_rate": round(cancellation_rate, 2),
            "total_revenue": str(total_revenue),
            "average_daily_bookings": round(avg_daily, 2),
        })
