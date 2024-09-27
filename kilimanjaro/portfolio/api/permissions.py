from rest_framework import permissions


class PortfolioPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "skilledworker")

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, "skilledworker"):
            if view.action in ["retrieve", "partial_update", "update"]:
                return obj.skilled_worker == request.user.skilledworker


class PortfolioImagePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "skilledworker")

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, "skilledworker"):
            if view.action in ["retrieve", "destroy", "partial_update", "update"]:
                return obj.portfolio.skilled_worker == request.user.skilledworker
