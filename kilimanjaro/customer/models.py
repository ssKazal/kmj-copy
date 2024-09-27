import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import models
from djmoney.models.fields import MoneyField
from model_utils.models import TimeStampedModel

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class Customer(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(
        "user.User", on_delete=models.CASCADE, verbose_name="user"
    )
    balance = MoneyField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):

        if self.id:

            # Removes and adds customer's cache data
            cache.delete(f"custom_profile_{self.user.id}")
            cache.set(f"custom_profile_{self.user.id}", self, timeout=CACHE_TTL)

        return super().save(*args, **kwargs)
