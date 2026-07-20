from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.appointments.models import Appointment

from .models import StaffProfile, TimeOff, WorkingHours
from .serializers import (
    StaffAvailabilitySlotSerializer,
    StaffProfileSerializer,
    TimeOffSerializer,
    WorkingHoursSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Staff"],
        summary="List staff profiles",
        description="Public endpoint. Returns all staff profiles with their offered services.",
        responses={200: StaffProfileSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Staff"],
        summary="Get staff profile detail",
        description="Public endpoint. Returns a single staff profile by ID.",
        responses={200: StaffProfileSerializer},
    ),
)
class StaffProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaffProfile.objects.select_related("user").prefetch_related(
        "services_offered"
    )
    serializer_class = StaffProfileSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(
        tags=["Staff"],
        summary="List working hours",
        description="Returns all working hour configurations.",
        responses={200: WorkingHoursSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Staff"],
        summary="Create working hours",
        description="Set working hours for a staff member.",
        responses={201: WorkingHoursSerializer},
    ),
)
class WorkingHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Staff"],
        summary="List time-off periods",
        description="Returns all configured time-off periods.",
        responses={200: TimeOffSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Staff"],
        summary="Create time-off period",
        description="Block a time period for a staff member.",
        responses={201: TimeOffSerializer},
    ),
)
class TimeOffViewSet(viewsets.ModelViewSet):
    queryset = TimeOff.objects.all()
    serializer_class = TimeOffSerializer


@extend_schema(
    tags=["Staff"],
    summary="Get staff availability for a date",
    description=(
        "Returns computed free time slots for a staff member on a given date. "
        "Slots are based on working hours minus existing bookings and time-off blocks."
    ),
    parameters=[
        OpenApiParameter(
            name="date",
            type=str,
            required=True,
            description="Date in YYYY-MM-DD format.",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "available_slots": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                    },
                },
            },
        },
        400: {"description": "Missing or invalid date parameter."},
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def staff_availability(request, staff_id):
    date_str = request.query_params.get("date")
    if not date_str:
        return Response(
            {"detail": "date parameter is required (YYYY-MM-DD)."}, status=400
        )

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    weekday = target_date.weekday()

    working_hours = WorkingHours.objects.filter(staff_id=staff_id, weekday=weekday)
    if not working_hours.exists():
        return Response({"date": date_str, "available_slots": []})

    time_offs = TimeOff.objects.filter(
        staff_id=staff_id,
        start_datetime__date__lte=target_date,
        end_datetime__date__gte=target_date,
    )

    day_start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))

    existing_bookings = Appointment.objects.filter(
        staff_id=staff_id,
        start_datetime__date=target_date,
        status__in=["pending", "confirmed"],
    ).values_list("start_datetime", "end_datetime")

    slots = []
    for wh in working_hours:
        slot_start = timezone.make_aware(datetime.combine(target_date, wh.start_time))
        slot_end = timezone.make_aware(datetime.combine(target_date, wh.end_time))

        current = slot_start
        while current < slot_end:
            next_slot = current + timedelta(minutes=30)
            if next_slot > slot_end:
                next_slot = slot_end

            is_available = True

            for to_start, to_end in time_offs.values_list(
                "start_datetime", "end_datetime"
            ):
                if current < to_end and next_slot > to_start:
                    is_available = False
                    break

            if is_available:
                for bk_start, bk_end in existing_bookings:
                    if current < bk_end and next_slot > bk_start:
                        is_available = False
                        break

            if is_available:
                slots.append({"start": current.time(), "end": next_slot.time()})

            current = next_slot

    serializer = StaffAvailabilitySlotSerializer(slots, many=True)
    return Response({"date": date_str, "available_slots": serializer.data})
