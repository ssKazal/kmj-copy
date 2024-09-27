from rest_framework import permissions


class NotificationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if view.action in ["retrieve", "partial_update", "mark_as_read"]:
                return obj.user == request.user
