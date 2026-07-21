from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_live(request):
    return Response({"status": "alive"})


@api_view(["GET"])
@permission_classes([AllowAny])
def health_ready(request):
    try:
        connection.ensure_connection()
        return Response({"status": "ready", "database": "connected"})
    except OperationalError:
        return Response(
            {"status": "unhealthy", "database": "disconnected"},
            status=503,
        )
