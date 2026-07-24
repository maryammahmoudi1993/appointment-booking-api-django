from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from core.permissions import IsAdminRole

from .admin_copilot import admin_chat
from .copilot import chat
from .serializers import CopilotRequestSerializer, CopilotResponseSerializer


class CopilotThrottle(UserRateThrottle):
    rate = "30/hour"
    scope = "copilot"


class CopilotView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CopilotThrottle]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CopilotRequestSerializer
        return CopilotResponseSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = chat(
            user_message=serializer.validated_data["message"],
            user=request.user,
            conversation_id=serializer.validated_data.get("conversation_id"),
        )

        return Response(
            CopilotResponseSerializer(
                {
                    "reply": result.reply,
                    "tool_calls_made": result.tool_calls_made,
                    "conversation_id": result.conversation_id,
                }
            ).data
        )


class AdminCopilotThrottle(UserRateThrottle):
    rate = "60/hour"
    scope = "admin-copilot"


class AdminCopilotView(generics.GenericAPIView):
    """Admin-only analytics copilot endpoint."""

    permission_classes = [IsAuthenticated, IsAdminRole]
    throttle_classes = [AdminCopilotThrottle]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CopilotRequestSerializer
        return CopilotResponseSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = admin_chat(
            message=serializer.validated_data["message"],
            user=request.user,
            conversation_id=serializer.validated_data.get("conversation_id"),
        )

        return Response({
            "reply": result.reply,
            "tool_calls_made": result.tool_calls_made,
        })
