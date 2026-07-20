from rest_framework import permissions


class IsOwnerOrStaffOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        if request.user.role == "staff":
            return obj.staff == request.user
        return obj.customer == request.user
