from rest_framework import viewsets

from .models import Service
from .permissions import IsAdminOrReadOnly
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name", "description")
    ordering_fields = ("name", "price", "duration_minutes")
