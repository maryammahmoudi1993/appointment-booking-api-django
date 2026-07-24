from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from core.mixins import BusinessScopedMixin

from .models import Service
from .permissions import IsAdminOrReadOnly
from .serializers import ServiceSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Services"],
        summary="List active services",
        description="Public endpoint. Returns all active services.",
        responses={200: ServiceSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Services"],
        summary="Get service detail",
        description="Public endpoint. Returns a single service by ID.",
        responses={200: ServiceSerializer},
    ),
    create=extend_schema(
        tags=["Services"],
        summary="Create a new service",
        description="Admin only. Create a new service offering.",
        responses={201: ServiceSerializer},
    ),
    update=extend_schema(
        tags=["Services"],
        summary="Update a service",
        description="Admin only. Full update of a service.",
        responses={200: ServiceSerializer},
    ),
    partial_update=extend_schema(
        tags=["Services"],
        summary="Partially update a service",
        description="Admin only. Partial update of a service.",
        responses={200: ServiceSerializer},
    ),
    destroy=extend_schema(
        tags=["Services"],
        summary="Delete a service",
        description="Admin only. Soft-delete by deactivating the service.",
        responses={204: None},
    ),
)
class ServiceViewSet(BusinessScopedMixin, viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name", "description")
    ordering_fields = ("name", "price", "duration_minutes")

    def perform_create(self, serializer):
        # ServiceSerializer deliberately excludes `business` from its writable
        # fields (no mass-assignment), but without assigning it here every
        # service created through this endpoint gets business=None and then
        # silently never appears in any business-scoped listing again.
        serializer.save(business=self.get_business())
