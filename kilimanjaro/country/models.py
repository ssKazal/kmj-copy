import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Country(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=225, null=True)
    currency_name = models.CharField(max_length=50, null=True)
    currency_code = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return str(self.name)
