from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )
    staff_name = serializers.CharField(source="staff.get_full_name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    has_review = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    promo_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
            "points_earned",
            "has_review",
            "discount_amount",
            "promo_code",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "status",
            "points_earned",
        )

    def get_has_review(self, obj) -> bool:
        return hasattr(obj, "review")

    def get_discount_amount(self, obj):
        redemption = getattr(obj, "promo_redemption", None)
        return str(redemption.discount_amount) if redemption else None

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
    has_review = serializers.SerializerMethodField()

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
            "points_earned",
            "has_review",
            "created_at",
        )

    def get_has_review(self, obj) -> bool:
        return hasattr(obj, "review")
