import secrets

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import ClientAPIKey

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


@receiver(pre_save, sender=ClientAPIKey)
def client_api_key(sender, instance, *args, **kwargs):
    """Initializes secrets key to api_key field"""

    # initialize api key when creates objects
    if not instance.api_key:
        while True:
            api_key = secrets.token_urlsafe(34)
            is_exists = ClientAPIKey.objects.filter(api_key=api_key).exists()
            if not is_exists:
                instance.api_key = secrets.token_urlsafe(34)
                break

    # set API keys to cache
    client_api_list = ClientAPIKey.objects.filter(is_active=True).values_list(
        "api_key", flat=True
    )
    cache.set("client_api_keys", client_api_list, timeout=CACHE_TTL)