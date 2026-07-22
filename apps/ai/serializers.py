from rest_framework import serializers


class CopilotRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, help_text="The user's message to the AI copilot.")


class CopilotResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    tool_calls_made = serializers.ListField(child=serializers.DictField(), required=False)
