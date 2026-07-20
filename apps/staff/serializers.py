from rest_framework import serializers

from .models import StaffProfile, TimeOff, WorkingHours


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
