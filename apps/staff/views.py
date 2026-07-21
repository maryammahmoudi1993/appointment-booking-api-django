from datetime import datetime, timedelta

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.appointments.models import Appointment
from core.permissions import IsAdminRole

from .models import StaffProfile, TimeOff, WorkingHours
from .serializers import (
    StaffAvailabilitySlotSerializer,
    StaffCreateSerializer,
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
    update=extend_schema(
        tags=["Staff"],
        summary="Update a staff profile",
        description="Admin only. Update bio and offered services.",
        responses={200: StaffProfileSerializer},
    ),
    partial_update=extend_schema(
        tags=["Staff"],
        summary="Partially update a staff profile",
        description="Admin only. Update bio and/or offered services.",
        responses={200: StaffProfileSerializer},
    ),
    destroy=extend_schema(
        tags=["Staff"],
        summary="Remove a staff profile",
        description="Admin only. Deletes the staff profile (not the underlying user account).",
        responses={204: None},
    ),
)
class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related("user").prefetch_related(
        "services_offered"
    )
    serializer_class = StaffProfileSerializer
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminRole()]

    @extend_schema(
        tags=["Staff"],
        summary="Add a new staff member",
        description=(
            "Admin only. Creates a User with role='staff' and its StaffProfile "
            "in one step, including bio and offered services."
        ),
        request=StaffCreateSerializer,
        responses={201: StaffProfileSerializer},
    )
    @action(detail=False, methods=["post"], url_path="onboard")
    def onboard(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(
            StaffProfileSerializer(profile).data, status=status.HTTP_201_CREATED
        )


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
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = super().get_queryset()
        staff_id = self.request.query_params.get("staff")
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset


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
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = super().get_queryset()
        staff_id = self.request.query_params.get("staff")
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset


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
                            "available": {"type": "boolean"},
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

            slots.append(
                {"start": current.time(), "end": next_slot.time(), "available": is_available}
            )

            current = next_slot

    serializer = StaffAvailabilitySlotSerializer(slots, many=True)
    return Response({"date": date_str, "available_slots": serializer.data})
