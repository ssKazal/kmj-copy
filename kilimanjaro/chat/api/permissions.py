from rest_framework import permissions


class ChatRoomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "block_chat_room", "unblock_chat_room", "blocked_chat_room_list"]:
                return True
        return False


class ChatmessagePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "report_message"]:
                return True
        return False