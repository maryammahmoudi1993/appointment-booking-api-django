from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.services.models import Service

from .models import StaffProfile, TimeOff, WorkingHours

User = get_user_model()


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ("id", "staff", "weekday", "start_time", "end_time")
        read_only_fields = ("id",)

    def validate_staff(self, value):
        if value.role != "staff":
            raise serializers.ValidationError("Assigned user must have role 'staff'.")
        return value


class TimeOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOff
        fields = ("id", "staff", "start_datetime", "end_datetime", "reason")
        read_only_fields = ("id",)

    def validate_staff(self, value):
        if value.role != "staff":
            raise serializers.ValidationError("Assigned user must have role 'staff'.")
        return value

    def validate(self, attrs):
        if attrs["start_datetime"] >= attrs["end_datetime"]:
            raise serializers.ValidationError(
                "End datetime must be after start datetime."
            )
        return attrs


class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields = ("id", "user", "username", "full_name", "bio", "services_offered")
        read_only_fields = ("id",)

    def get_full_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username

    def validate_user(self, value):
        if value.role != "staff":
            raise serializers.ValidationError("Assigned user must have role 'staff'.")
        return value


class StaffAvailabilitySlotSerializer(serializers.Serializer):
    start = serializers.TimeField()
    end = serializers.TimeField()


class StaffCreateSerializer(serializers.Serializer):
    """Admin-only: create a User(role='staff') and its StaffProfile together."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=""
    )
    password = serializers.CharField(write_only=True, min_length=8)
    bio = serializers.CharField(required=False, allow_blank=True, default="")
    services_offered = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, required=False, default=list
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def create(self, validated_data):
        services = validated_data.pop("services_offered", [])
        password = validated_data.pop("password")
        bio = validated_data.pop("bio", "")
        user = User(role="staff", **validated_data)
        user.set_password(password)
        user.save()
        profile = StaffProfile.objects.create(user=user, bio=bio)
        if services:
            profile.services_offered.set(services)
        return profile
