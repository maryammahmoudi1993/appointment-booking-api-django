from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "engagement"

router = DefaultRouter()
router.register("reviews", views.ReviewViewSet, basename="review")
router.register(
    "loyalty/rewards", views.LoyaltyRewardViewSet, basename="loyalty-reward"
)
router.register("promotions", views.PromoCodeViewSet, basename="promotion")
router.register(
    "promo-redemptions", views.PromoRedemptionViewSet, basename="promo-redemption"
)
router.register(
    "support-messages", views.SupportMessageViewSet, basename="support-message"
)

urlpatterns = [
    path(
        "loyalty/summary/", views.LoyaltySummaryView.as_view(), name="loyalty-summary"
    ),
    path("", include(router.urls)),
]
