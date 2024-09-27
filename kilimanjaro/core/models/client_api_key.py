import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class ClientAPIKey(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    api_key = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Client API Key"
        verbose_name_plural = "Client API Keys"

    def __str__(self):
        return str(self.api_key)
