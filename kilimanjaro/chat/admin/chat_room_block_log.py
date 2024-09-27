from django.contrib import admin
from chat.models import ChatRoomBlockLog

from core.utils.general_func import admin_list_page_action


class ChatRoomBlockLogAdmin(admin.ModelAdmin):
    """
    Represents ChatRoomBlockLog admin
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ChatRoomBlockLog

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "block_type", 
        "blocked_by_user",
        "blocked_to_user"
    ]
    search_fields = [
        "blocked_by_user__first_name",
        "blocked_by_user__last_name",
        "blocked_by_user__email",
        "blocked_by_user__username",
        "blocked_to_user__first_name",
        "blocked_to_user__last_name",
        "blocked_to_user__email",
        "blocked_to_user__username",
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
                            "chatroomblocklog.change_chatroomblocklog"
                        ),
                        "path": f"/chat/chatroomblocklog/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "chatroomblocklog.delete_chatroomblocklog"
                        ),
                        "path": f"/chat/chatroomblocklog/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "chatroomblocklog.delete_chatroomblocklog"
        ) or request.user.has_perm("chatroomblocklog.change_chatroomblocklog"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ChatRoomBlockLog, ChatRoomBlockLogAdmin)



