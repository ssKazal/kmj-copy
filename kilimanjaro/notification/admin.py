from django.contrib import admin

from core.utils.general_func import admin_list_page_action
from notification.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    """
    Represents Notification admin

    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = Notification

    readonly_fields = [
        "uuid",
    ]
    list_display = ["id", "uuid", "notification_for", "user", "is_read", "body"]
    search_fields = ["notification_for", "user__first_name", "user__last_name"]
    list_filter = [
        "is_read",
    ]
    autocomplete_fields = [
        "user",
    ]

    def get_list_display(self, request):
        """Overriding list display"""

        default_list_display = super(NotificationAdmin, self).get_list_display(request)

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "notification.change_notification"
                        ),
                        "path": f"/notification/notification/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "notification.delete_notification"
                        ),
                        "path": f"/notification/notification/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "notification.delete_notification"
        ) or request.user.has_perm("notification.change_notification"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(Notification, NotificationAdmin)
admin.autodiscover()
admin.site.enable_nav_sidebar = False
