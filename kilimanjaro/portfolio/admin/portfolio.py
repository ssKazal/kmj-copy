from django.contrib import admin

from certification.models import Certification
from core.utils.general_func import admin_list_page_action
from portfolio.models import Portfolio


class PortfolioAdmin(admin.ModelAdmin):
    """
    Represents Portfolio admin

    Methods
    --------
    get_list_display(self, request):
        overriding list display
    """

    model = Portfolio

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "skilled_worker",
        "education",
        "certification",
    ]
    search_fields = [
        "education",
    ]
    autocomplete_fields = [
        "skilled_worker",
    ]

    def get_list_display(self, request):
        """overriding list display"""

        default_list_display = super(PortfolioAdmin, self).get_list_display(request)

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm("portfolio.change_portfolio"),
                        "path": f"/portfolio/portfolio/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm("portfolio.delete_portfolio"),
                        "path": f"/portfolio/portfolio/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("portfolio.delete_portfolio") or request.user.has_perm(
            "portfolio.change_portfolio"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display

    # when skilled worker adding portfolio only show this skilled worker certification
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = (
            request.META["PATH_INFO"].rstrip("/change/").split("/")[-1]
        )  # get user id from path

        if db_field.name == "certification" and obj_id.isdigit():
            obj = self.get_object(request, obj_id)

            if obj:
                # Assigning certification queryset to "certification" select field
                kwargs["queryset"] = Certification.objects.filter(
                    skilled_worker=obj.skilled_worker
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Portfolio, PortfolioAdmin)
