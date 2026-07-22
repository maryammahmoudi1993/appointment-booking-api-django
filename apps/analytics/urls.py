from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("analytics/revenue/", views.RevenueAnalyticsView.as_view(), name="analytics-revenue"),
    path("analytics/staff/", views.StaffAnalyticsView.as_view(), name="analytics-staff"),
    path("analytics/services/", views.ServiceAnalyticsView.as_view(), name="analytics-services"),
    path("analytics/bookings/", views.BookingAnalyticsView.as_view(), name="analytics-bookings"),
]
