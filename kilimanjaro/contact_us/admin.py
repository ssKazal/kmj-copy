from django.contrib import admin

from contact_us.models import ContactUs
from core.utils.general_func import admin_list_page_action


class ContactUsAdmin(admin.ModelAdmin):
    """
    Represents ContactUs admin

    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = ContactUs

    readonly_fields = [
        "uuid",
    ]
    list_display = ["id", "uuid", "title", "user", "resolved"]
    list_filter = [
        "resolved",
    ]
    search_fields = [
        "title",
    ]
    autocomplete_fields = [
        "user",
    ]

    def get_list_display(self, request):
        """Overrides list display column"""

        default_list_display = super(ContactUsAdmin, self).get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm("contactus.change_contactus"),
                        "path": f"/contact_us/contactus/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm("contactus.delete_contactus"),
                        "path": f"/contact_us/contactus/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("contactus.delete_contactus") or request.user.has_perm(
            "contactus.change_contactus"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ContactUs, ContactUsAdmin)
