from rest_framework import permissions

from core.business import get_user_business


class IsBusinessMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return get_user_business(request.user) is not None


class IsBusinessAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        business = get_user_business(request.user)
        if business is None:
            return False
        return business.memberships.filter(
            user=request.user, role__in=["admin", "manager"]
        ).exists()
