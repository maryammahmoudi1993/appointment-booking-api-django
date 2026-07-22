from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .copilot import chat
from .serializers import CopilotRequestSerializer, CopilotResponseSerializer


class CopilotView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

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
