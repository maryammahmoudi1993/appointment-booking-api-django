from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )
    staff_name = serializers.CharField(source="staff.get_full_name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "customer",
            "customer_name",
            "staff",
            "staff_name",
            "service",
            "service_name",
            "start_datetime",
            "end_datetime",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "status")

    def validate_customer(self, value):
        if value.role != "customer":
            raise serializers.ValidationError(
                "Assigned user must have role 'customer'."
            )
        return value

    def validate_staff(self, value):
        if value.role != "staff":
            raise serializers.ValidationError("Assigned user must have role 'staff'.")
        return value


class AppointmentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )
    staff_name = serializers.CharField(source="staff.get_full_name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "customer",
            "customer_name",
            "staff",
            "staff_name",
            "service",
            "service_name",
            "start_datetime",
            "end_datetime",
            "status",
            "created_at",
        )
