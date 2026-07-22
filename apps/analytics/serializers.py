from rest_framework import serializers


class RevenuePointSerializer(serializers.Serializer):
    period = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    bookings = serializers.IntegerField()


class RevenueSummarySerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_bookings = serializers.IntegerField()
    average_ticket = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_by_period = RevenuePointSerializer(many=True)


class StaffAnalyticsSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    staff_name = serializers.CharField()
    total_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.FloatField(allow_null=True)
    review_count = serializers.IntegerField()


class ServiceAnalyticsSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    total_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.FloatField(allow_null=True)
    review_count = serializers.IntegerField()
    average_duration = serializers.IntegerField()


class BookingSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    confirmed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    cancellation_rate = serializers.FloatField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_daily_bookings = serializers.FloatField()
