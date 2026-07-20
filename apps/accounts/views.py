from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        summary="Register a new user",
        description="Create a new user account and return JWT tokens.",
        responses={201: {"description": "User created with tokens"}},
    ),
)
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        summary="Logout (blacklist refresh token)",
        description="Blacklist a refresh token to invalidate it.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
            }
        },
        responses={200: "Successfully logged out.", 400: "Invalid token."},
    ),
)
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema_view(
    get=extend_schema(
        tags=["Auth"],
        summary="Get current user profile",
        description="Retrieve the authenticated user's profile.",
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        tags=["Auth"],
        summary="Update current user profile",
        description="Partially update the authenticated user's profile.",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
)
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
