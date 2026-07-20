from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .throttles import AuthRateThrottle

app_name = "accounts"

urlpatterns = [
    path(
        "auth/register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "auth/login/",
        TokenObtainPairView.as_view(throttle_classes=[AuthRateThrottle]),
        name="token_obtain_pair",
    ),
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(throttle_classes=[AuthRateThrottle]),
        name="token_refresh",
    ),
    path(
        "auth/logout/",
        views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "auth/me/",
        views.MeView.as_view(),
        name="me",
    ),
]
