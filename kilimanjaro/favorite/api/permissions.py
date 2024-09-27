from rest_framework import permissions


class FavoritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "customer")

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, "customer"):
            if view.action in ["retrieve", "destroy", "partial_update", "update"]:
                return obj.customer == request.user.customer
