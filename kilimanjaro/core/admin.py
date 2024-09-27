from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.contrib import admin

from core.models import ClientAPIKey
from core.utils.general_func import admin_list_page_action

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class ClientAPIKeyAdmin(admin.ModelAdmin):
    """
    Represents ClientAPIKey admin

    Methods
    --------
    get_list_display(self, request):
        Overrides list display column
    """

    model = ClientAPIKey

    readonly_fields = [
        "uuid",
        "api_key"
    ]
    list_display = ["id", "uuid", "api_key", "created", "is_active"]
    search_fields = [
        "api_key",
    ]

    def get_list_display(self, request):
        """Overrides list display"""

        default_list_display = super(ClientAPIKeyAdmin, self).get_list_display(request)

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "customer.change_clientapikey"
                        ),
                        "path": f"/core/clientapikey/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "customer.delete_clientapikey"
                        ),
                        "path": f"/core/clientapikey/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("customer.delete_customer") or request.user.has_perm(
            "customer.change_customer"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display

    def delete_model(self, request, obj) -> None:
        """ Initializes secrets key to api_key field """

        # removes API keys from cache
        client_api_list = ClientAPIKey.objects.filter(is_active=True).values_list('api_key', flat=True)
        cache.set(
            f"client_api_keys", client_api_list, timeout=CACHE_TTL
        )
        return super().delete_model(request, obj)

    def save_model(self, request, obj, form, change) -> None:
        """overrides save method for update chache"""
        
        # update API keys in cache
        client_api_list = ClientAPIKey.objects.filter(is_active=True).values_list('api_key', flat=True)
        cache.set(
            f"client_api_keys", client_api_list, timeout=CACHE_TTL
        )
        return super().save_model(request, obj, form, change)

admin.site.register(ClientAPIKey, ClientAPIKeyAdmin)

