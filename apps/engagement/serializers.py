from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.services.models import Service

from .models import LoyaltyReward, LoyaltyRedemption, PromoCode, Review, SupportMessage


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )
    staff_name = serializers.CharField(source="staff.get_full_name", read_only=True)
    service_name = serializers.CharField(
        source="appointment.service.name", read_only=True
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "appointment",
            "customer",
            "customer_name",
            "staff",
            "staff_name",
            "service_name",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "customer", "staff", "created_at")

    def validate_appointment(self, appointment: Appointment):
        request = self.context["request"]
        if appointment.customer_id != request.user.id:
            raise serializers.ValidationError(
                "You can only review your own appointments."
            )
        if appointment.status != "completed":
            raise serializers.ValidationError(
                "Only completed appointments can be reviewed."
            )
        if hasattr(appointment, "review"):
            raise serializers.ValidationError(
                "This appointment has already been reviewed."
            )
        return appointment

    def create(self, validated_data):
        appointment = validated_data["appointment"]
        validated_data["customer"] = appointment.customer
        validated_data["staff"] = appointment.staff
        return super().create(validated_data)


class LoyaltyRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyReward
        fields = ("id", "name", "description", "points_cost", "is_active")
        read_only_fields = ("id",)


class LoyaltyRedemptionSerializer(serializers.ModelSerializer):
    reward_name = serializers.CharField(source="reward.name", read_only=True)

    class Meta:
        model = LoyaltyRedemption
        fields = ("id", "reward", "reward_name", "points_spent", "created_at")
        read_only_fields = ("id", "points_spent", "created_at")


class PromoCodeSerializer(serializers.ModelSerializer):
    times_redeemed = serializers.SerializerMethodField()
    revenue_influenced = serializers.SerializerMethodField()
    services = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, required=False
    )
    service_names = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = (
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "services",
            "service_names",
            "is_active",
            "max_redemptions",
            "starts_at",
            "ends_at",
            "times_redeemed",
            "revenue_influenced",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_times_redeemed(self, obj) -> int:
        return obj.redemptions.count()

    def get_service_names(self, obj) -> list:
        return [s.name for s in obj.services.all()]

    def get_revenue_influenced(self, obj) -> str:
        total = sum(
            (r.appointment.service.price for r in obj.redemptions.all() if r.appointment),
            start=0,
        )
        return str(total)


class PromoValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), required=False
    )


class SupportMessageSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )

    class Meta:
        model = SupportMessage
        fields = (
            "id",
            "customer",
            "customer_name",
            "message",
            "is_read",
            "admin_reply",
            "replied_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "is_read",
            "admin_reply",
            "replied_at",
            "created_at",
        )
