from django.contrib import admin

from certification.models import Certification
from core.utils.general_func import admin_list_page_action


class CertificationAdmin(admin.ModelAdmin):
    """
    Represents Certification admin
    
    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = Certification

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "certification_name",
        "skilled_worker",
        "date_earned",
        "certification_issued",
    ]
    search_fields = [
        "certification_name",
    ]
    autocomplete_fields = [
        "skilled_worker",
    ]

    def get_list_display(self, request):
        """Overrides list display column"""

        default_list_display = super(CertificationAdmin, self).get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "certification.change_certification"
                        ),
                        "path": f"/certification/certification/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "certification.delete_certification"
                        ),
                        "path": f"/certification/certification/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "certification.delete_certification"
        ) or request.user.has_perm("certification.change_certification"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(Certification, CertificationAdmin)
