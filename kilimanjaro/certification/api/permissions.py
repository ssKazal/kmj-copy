from rest_framework import permissions


class CertificationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "skilledworker")

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, "skilledworker"):
            if view.action in ["retrieve", "destroy", "partial_update", "update"]:
                return obj.skilled_worker == request.user.skilledworker
