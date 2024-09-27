import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Favorite(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, verbose_name="customer"
    )
    skilled_worker = models.ForeignKey(
        "skilled_worker.SkilledWorker",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="skilled worker",
    )

    class Meta:
        unique_together = ("customer", "skilled_worker")

    def __str__(self):
        return str(self.id)
