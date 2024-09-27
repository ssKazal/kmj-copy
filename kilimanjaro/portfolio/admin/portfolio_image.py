from django.contrib import admin

from core.utils.general_func import admin_list_page_action
from portfolio.models import PortfolioImage


class PortfolioImageAdmin(admin.ModelAdmin):
    """
    Represents PortfolioImage admin

    Methods
    --------
    get_list_display(self, request):
        Overriding list display
    """

    model = PortfolioImage

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "portfolio",
    ]
    autocomplete_fields = [
        "portfolio",
    ]

    def get_list_display(self, request):
        """Overriding list display"""

        default_list_display = super(PortfolioImageAdmin, self).get_list_display(
            request
        )

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "portfolio.change_portfolioimage"
                        ),
                        "path": f"/portfolio/portfolioimage/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "portfolio.delete_portfolioimage"
                        ),
                        "path": f"/portfolio/portfolioimage/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "portfolio.delete_portfolioimage"
        ) or request.user.has_perm("portfolio.change_portfolioimage"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(PortfolioImage, PortfolioImageAdmin)
