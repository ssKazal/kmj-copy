import uuid

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import models
from djmoney.models.fields import MoneyField
from model_utils.models import TimeStampedModel

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class SkilledWorkerManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        """While creating an SW, a 'Portfolio' object for that
        SW have to create, so we need to extend the 'bulk_create' method"""

        skilled_worker_objs = super().bulk_create(
            objs, **kwargs
        )  # 'skilled worker' objects list
        Portfolio = apps.get_model("portfolio.Portfolio")
        portfolio_obj_list = []  # Initial 'portfolio' object will append here

        for obj in objs:
            portfolio_obj = Portfolio(skilled_worker=obj)
            portfolio_obj_list.append(portfolio_obj)

        Portfolio.objects.bulk_create(portfolio_obj_list)
        return skilled_worker_objs


class SkilledWorker(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(
        "user.User", on_delete=models.CASCADE, verbose_name="user"
    )
    occupation = models.ForeignKey(
        "occupation.Occupation",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="occupation",
    )
    description = models.TextField(max_length=2000, null=True)
    experience = models.IntegerField(null=True)
    balance = MoneyField(max_digits=10, decimal_places=2, null=True)

    objects = SkilledWorkerManager()

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):

        if self.id:

            # Removes & updates 'skilled worker' data from cache
            cache.delete(f"skilled_worker_profile{self.user.id}")
            cache.set(f"skilled_worker_profile{self.user.id}", self, timeout=CACHE_TTL)

        return super().save(*args, **kwargs)
