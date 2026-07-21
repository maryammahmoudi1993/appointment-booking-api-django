from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Appointment
from core.mixins import BusinessScopedMixin
from core.permissions import IsAdminRole, IsCustomerRole

from .models import (
    LoyaltyRedemption,
    LoyaltyReward,
    PromoCode,
    PromoRedemption,
    Review,
    SupportMessage,
)
from .serializers import (
    LoyaltyRedemptionSerializer,
    LoyaltyRewardSerializer,
    PromoCodeSerializer,
    PromoRedemptionSerializer,
    PromoValidateSerializer,
    ReviewSerializer,
    SupportMessageSerializer,
)
from .services import PromoCodeError, validate_promo_code


@extend_schema_view(
    list=extend_schema(
        tags=["Reviews"],
        summary="List reviews",
        description="Public. Optionally filter by ?staff=<user_id>.",
    ),
    create=extend_schema(
        tags=["Reviews"],
        summary="Leave a review",
        description="Customer only, for their own completed appointments.",
    ),
)
class ReviewViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = Review.objects.select_related("customer", "staff", "appointment__service")
    serializer_class = ReviewSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def perform_create(self, serializer):
        serializer.save(business=self.get_business())

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerRole()]
        return [IsAdminRole()]

    def get_queryset(self):
        queryset = super().get_queryset()
        staff_id = self.request.query_params.get("staff")
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Loyalty"], summary="List reward catalog"),
    create=extend_schema(tags=["Loyalty"], summary="Add a reward (admin)"),
)
class LoyaltyRewardViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = LoyaltyReward.objects.all()
    serializer_class = LoyaltyRewardSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        if self.action == "redeem":
            return [IsAuthenticated(), IsCustomerRole()]
        return [IsAdminRole()]

    @extend_schema(
        tags=["Loyalty"],
        summary="Redeem a reward",
        description="Customer only. Fails if balance is below the reward's point cost.",
        responses={201: LoyaltyRedemptionSerializer, 400: "Insufficient points"},
    )
    @action(detail=True, methods=["post"], url_path="redeem")
    def redeem(self, request, pk=None):
        reward = self.get_object()
        if not reward.is_active:
            return Response(
                {"detail": "This reward is not currently available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        balance = _loyalty_balance(request.user)
        if balance < reward.points_cost:
            return Response(
                {"detail": "Not enough points to redeem this reward."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        business = self.get_business()
        redemption = LoyaltyRedemption.objects.create(
            customer=request.user, reward=reward, points_spent=reward.points_cost,
            business=business,
        )
        return Response(
            LoyaltyRedemptionSerializer(redemption).data, status=status.HTTP_201_CREATED
        )


def _loyalty_balance(user) -> int:
    earned = (
        Appointment.objects.filter(customer=user, status="completed").aggregate(
            total=Sum("points_earned")
        )["total"]
        or 0
    )
    spent = (
        LoyaltyRedemption.objects.filter(customer=user).aggregate(total=Sum("points_spent"))[
            "total"
        ]
        or 0
    )
    return earned - spent


@extend_schema(
    tags=["Loyalty"],
    summary="Get my loyalty summary",
    description="Authenticated customer's points balance, earning history, and redemptions.",
)
class LoyaltySummaryView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerRole]

    def get(self, request):
        earned_appointments = Appointment.objects.filter(
            customer=request.user, status="completed", points_earned__gt=0
        ).select_related("service").order_by("-start_datetime")
        redemptions = LoyaltyRedemption.objects.filter(
            customer=request.user
        ).select_related("reward")

        history = [
            {
                "appointment": a.id,
                "service_name": a.service.name,
                "points": a.points_earned,
                "date": a.start_datetime,
            }
            for a in earned_appointments
        ]
        return Response(
            {
                "balance": _loyalty_balance(request.user),
                "history": history,
                "redemptions": LoyaltyRedemptionSerializer(redemptions, many=True).data,
            }
        )


@extend_schema_view(
    list=extend_schema(tags=["Promotions"], summary="List promo campaigns (admin)"),
    create=extend_schema(tags=["Promotions"], summary="Create a promo campaign (admin)"),
)
class PromoCodeViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer

    def get_permissions(self):
        if self.action == "validate":
            return [IsAuthenticated()]
        return [IsAdminRole()]

    @extend_schema(
        tags=["Promotions"],
        summary="Validate a promo code",
        description="Authenticated. Returns the discount preview without redeeming it.",
        request=PromoValidateSerializer,
    )
    @action(detail=False, methods=["post"], url_path="validate")
    def validate(self, request):
        serializer = PromoValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            promo = validate_promo_code(
                serializer.validated_data["code"],
                service=serializer.validated_data.get("service"),
            )
        except PromoCodeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "code": promo.code,
                "discount_type": promo.discount_type,
                "discount_value": str(promo.discount_value),
            }
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Promotions"],
        summary="List promo redemptions (admin)",
        description="Admin only. Shows all promo code redemptions.",
    ),
)
class PromoRedemptionViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = PromoRedemption.objects.select_related("promo", "customer", "appointment")
    serializer_class = PromoRedemptionSerializer
    http_method_names = ["get", "head", "options"]

    def get_permissions(self):
        return [IsAdminRole()]


@extend_schema_view(
    list=extend_schema(
        tags=["Support"],
        summary="List support messages",
        description="Admin sees every message (inbox); customers see only their own.",
    ),
    create=extend_schema(
        tags=["Support"],
        summary="Send a message to the admin",
        description="Authenticated customer sends a message that lands in the admin inbox.",
    ),
)
class SupportMessageViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = SupportMessage.objects.select_related("customer")
    serializer_class = SupportMessageSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "reply":
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == "admin":
            return queryset
        return queryset.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user, business=self.get_business())

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == "admin" and not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=["is_read"])
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Support"],
        summary="Reply to a support message",
        description="Admin only.",
        request={"application/json": {"type": "object", "properties": {"reply": {"type": "string"}}}},
        responses={200: SupportMessageSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reply")
    def reply(self, request, pk=None):
        message = self.get_object()
        reply_text = request.data.get("reply", "").strip()
        if not reply_text:
            return Response(
                {"detail": "Reply text is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        message.admin_reply = reply_text
        message.replied_at = timezone.now()
        message.is_read = True
        message.save(update_fields=["admin_reply", "replied_at", "is_read"])
        return Response(SupportMessageSerializer(message).data)
