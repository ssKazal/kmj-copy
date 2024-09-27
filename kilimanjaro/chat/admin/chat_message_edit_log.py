from django.contrib import admin
from chat.models import ChatMessageEditLog

from core.utils.general_func import admin_list_page_action


class ChatMessageEditLogAdmin(admin.ModelAdmin):
    """
    Represents Chat admin
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ChatMessageEditLog

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "message", 
        "previous_text_message",
        "message_text"
    ]
    search_fields = [
        "message__id"
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
                            "chatmessageeditlog.change_chatmessageeditlog"
                        ),
                        "path": f"/chat/chatmessageeditlog/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "chatmessageeditlog.delete_chatmessageeditlog"
                        ),
                        "path": f"/chat/chatmessageeditlog/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "chatmessageeditlog.delete_chatmessageeditlog"
        ) or request.user.has_perm("chatmessageeditlog.change_chatmessageeditlog"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ChatMessageEditLog, ChatMessageEditLogAdmin)



