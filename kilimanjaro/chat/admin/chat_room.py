from django.contrib import admin
from chat.models import ChatRoom

from core.utils.general_func import admin_list_page_action


class ChatRoomAdmin(admin.ModelAdmin):
    """
    Represents Chat admin
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ChatRoom

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "room_member_1",
        "room_member_2",
        "is_blocked_by_member_1",
        "is_blocked_by_member_2",
    ]
    search_fields = [
        "room_member_1__first_name",
        "room_member_1__last_name",
        "room_member_1__email",
        "room_member_1__username",
        "room_member_2__first_name",
        "room_member_2__last_name",
        "room_member_2__email",
        "room_member_2__username",
    ]

    def get_list_display(self, request):
        """Overrides list display column"""

        default_list_display = super().get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "chatroom.change_chatroom"
                        ),
                        "path": f"/chat/chatroom/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "chatroom.delete_chatroom"
                        ),
                        "path": f"/chat/chatroom/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "chatroom.delete_chatroom"
        ) or request.user.has_perm("chatroom.change_chatroom"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ChatRoom, ChatRoomAdmin)



