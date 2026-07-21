from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.engagement.models import PromoRedemption
from apps.engagement.services import (
    PromoCodeError,
    compute_discount,
    validate_promo_code,
)

from .models import Appointment
from .permissions import IsOwnerOrStaffOrAdmin
from .serializers import AppointmentListSerializer, AppointmentSerializer
from .validators import create_appointment_atomic, update_appointment_atomic


class AppointmentFilter(filters.FilterSet):
    date_from = filters.DateTimeFilter(field_name="start_datetime", lookup_expr="gte")
    date_to = filters.DateTimeFilter(field_name="start_datetime", lookup_expr="lte")
    staff = filters.NumberFilter(field_name="staff_id")
    service = filters.NumberFilter(field_name="service_id")
    status = filters.CharFilter(field_name="status")

    class Meta:
        model = Appointment
        fields = ["status", "date_from", "date_to", "staff", "service"]


@extend_schema_view(
    list=extend_schema(
        tags=["Appointments"],
        summary="List appointments",
        description=(
            "Role-scoped appointment list. Customers see their own bookings, "
            "staff see assigned bookings, admins see all. Supports filtering by "
            "status, date range, staff, and service."
        ),
        responses={200: AppointmentListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Appointments"],
        summary="Get appointment detail",
        description="Returns a single appointment by ID. Object-level permission check.",
        responses={200: AppointmentSerializer},
    ),
    create=extend_schema(
        tags=["Appointments"],
        summary="Create a new booking",
        description=(
            "Create an appointment. Runs full conflict-check inside a DB transaction "
            "with select_for_update to prevent race conditions. Returns 409 on conflict."
        ),
        responses={201: AppointmentSerializer, 409: "Booking conflict"},
    ),
    update=extend_schema(
        tags=["Appointments"],
        summary="Update/reschedule an appointment",
        description="Full update. Re-runs conflict-check logic inside a transaction.",
        responses={200: AppointmentSerializer, 409: "Booking conflict"},
    ),
    partial_update=extend_schema(
        tags=["Appointments"],
        summary="Partially update an appointment",
        description="Partial update. Re-runs conflict-check logic inside a transaction.",
        responses={200: AppointmentSerializer, 409: "Booking conflict"},
    ),
    destroy=extend_schema(
        tags=["Appointments"],
        summary="Delete an appointment",
        description="Hard-delete an appointment. Consider using cancel instead.",
        responses={204: None},
    ),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaffOrAdmin]
    filterset_class = AppointmentFilter
    search_fields = ("customer__username", "staff__username", "service__name")
    ordering_fields = ("start_datetime", "status", "created_at")

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Appointment.objects.select_related(
                "customer", "staff", "service"
            ).all()
        elif user.role == "staff":
            return Appointment.objects.select_related(
                "customer", "staff", "service"
            ).filter(staff=user)
        return Appointment.objects.select_related(
            "customer", "staff", "service"
        ).filter(customer=user)

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentListSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        promo_code = data.pop("promo_code", None)
        promo = None
        if promo_code:
            try:
                promo = validate_promo_code(promo_code, service=data["service"])
            except PromoCodeError as exc:
                raise serializers.ValidationError({"promo_code": [str(exc)]})

        appointment = create_appointment_atomic(
            customer_id=data["customer"].id,
            staff_id=data["staff"].id,
            service_id=data["service"].id,
            start_datetime=data["start_datetime"],
            end_datetime=data["end_datetime"],
            notes=data.get("notes", ""),
        )
        if promo:
            PromoRedemption.objects.create(
                promo=promo,
                customer=appointment.customer,
                appointment=appointment,
                discount_amount=compute_discount(promo, appointment.service.price),
            )
        serializer.instance = appointment

    def perform_update(self, serializer):
        data = serializer.validated_data
        appointment = update_appointment_atomic(
            appointment_id=serializer.instance.id,
            staff_id=data["staff"].id,
            service_id=data["service"].id,
            start_datetime=data["start_datetime"],
            end_datetime=data["end_datetime"],
        )
        serializer.instance = appointment

    @extend_schema(
        tags=["Appointments"],
        summary="Cancel an appointment",
        description="Soft-cancel. Sets status to 'cancelled'. Cannot cancel already cancelled/completed appointments.",
        responses={200: AppointmentSerializer, 400: "Cannot cancel"},
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status in ["cancelled", "completed"]:
            return Response(
                {"detail": f"Cannot cancel a {appointment.status} appointment."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        appointment.status = "cancelled"
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(
        tags=["Appointments"],
        summary="Confirm an appointment",
        description="Staff/admin only. Sets status from 'pending' to 'confirmed'.",
        responses={200: AppointmentSerializer, 403: "Forbidden", 400: "Not pending"},
    )
    @action(detail=True, methods=["patch"], url_path="confirm")
    def confirm(self, request, pk=None):
        if request.user.role not in ["staff", "admin"]:
            return Response(
                {"detail": "Only staff or admin can confirm appointments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        appointment = self.get_object()
        if appointment.status != "pending":
            return Response(
                {"detail": "Only pending appointments can be confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        appointment.status = "confirmed"
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(
        tags=["Appointments"],
        summary="Complete an appointment",
        description=(
            "Staff/admin only. Sets status from 'confirmed' to 'completed' and "
            "awards loyalty points to the customer based on the service price."
        ),
        responses={200: AppointmentSerializer, 403: "Forbidden", 400: "Not confirmed"},
    )
    @action(detail=True, methods=["patch"], url_path="complete")
    def complete(self, request, pk=None):
        if request.user.role not in ["staff", "admin"]:
            return Response(
                {"detail": "Only staff or admin can complete appointments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        appointment = self.get_object()
        if appointment.status != "confirmed":
            return Response(
                {"detail": "Only confirmed appointments can be completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        appointment.status = "completed"
        appointment.points_earned = int(appointment.service.price)
        appointment.save(update_fields=["status", "points_earned", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)
