from django.contrib import admin
from chat.models import ChatMessage

from core.utils.general_func import admin_list_page_action


class ChatMessageAdmin(admin.ModelAdmin):
    """
    Represents Chat admin
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ChatMessage

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "sender",
        "receiver",
        "room",
        "message_text",
        "attachment_links",
        "voice",
        "is_deleted"
    ]
    search_fields = [
        "sender__first_name",
        "sender__last_name",
        "sender__email",
        "sender__username",
        "receiver__first_name",
        "receiver__last_name",
        "receiver__email",
        "receiver__username",
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
                            "chatmessage.change_chatmessage"
                        ),
                        "path": f"/chat/chatmessage/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "chatmessage.delete_chatmessage"
                        ),
                        "path": f"/chat/chatmessage/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "chatmessage.delete_chatmessage"
        ) or request.user.has_perm("chatmessage.change_chatmessage"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ChatMessage, ChatMessageAdmin)



