from django.contrib import admin
from chat.models import ChatMessageReport

from core.utils.general_func import admin_list_page_action


class ChatMessageReportAdmin(admin.ModelAdmin):
    """
    Represents Chat Message Report
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ChatMessageReport

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "reported_by",
        "message",
        "reason"
    ]
    search_fields = [
        "reported_by__first_name",
        "reported_by__last_name",
        "reported_by__email",
        "reported_by__username",
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
                            "chatmessagereport.change_chatmessagereport"
                        ),
                        "path": f"/chat/chatmessagereport/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "chatmessagereport.delete_chatmessagereport"
                        ),
                        "path": f"/chat/chatmessagereport/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "chatmessagereport.delete_chatmessagereport"
        ) or request.user.has_perm("chatmessagereport.change_chatmessagereport"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ChatMessageReport, ChatMessageReportAdmin)



