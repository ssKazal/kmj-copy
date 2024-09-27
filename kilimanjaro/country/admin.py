from django.contrib import admin

from core.utils.general_func import admin_list_page_action
from country.models import Country


class CountryAdmin(admin.ModelAdmin):
    """
    Represents Country admin

    Methods
    --------
    get_list_display(self, request):
        Adding custom action button to country list item
    """

    model = Country

    readonly_fields = [
        "uuid",
    ]
    list_display = ["id", "uuid", "name", "currency_name", "currency_code"]
    search_fields = ["name", "currency_name", "currency_code"]

    def get_list_display(self, request):
        """Adding custom action button to country list item"""

        default_list_display = super(CountryAdmin, self).get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm("country.change_country"),
                        "path": f"/country/country/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm("country.delete_country"),
                        "path": f"/country/country/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("country.delete_country") or request.user.has_perm(
            "country.change_country"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(Country, CountryAdmin)

admin.autodiscover()
admin.site.enable_nav_sidebar = False
