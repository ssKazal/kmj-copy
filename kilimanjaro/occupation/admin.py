from django.contrib import admin

from core.utils.general_func import admin_list_page_action
from occupation.models import Occupation


class OccupationAdmin(admin.ModelAdmin):
    """
    Represents Occupation admin

    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = Occupation

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "name",
    ]
    search_fields = ["name"]

    def get_list_display(self, request):
        """Overriding list display"""

        default_list_display = super(OccupationAdmin, self).get_list_display(request)

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "occupation.change_occupation"
                        ),
                        "path": f"/occupation/occupation/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "occupation.delete_occupation"
                        ),
                        "path": f"/occupation/occupation/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "occupation.delete_occupation"
        ) or request.user.has_perm("occupation.change_occupation"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(Occupation, OccupationAdmin)
