import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Certification(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    skilled_worker = models.ForeignKey(
        "skilled_worker.SkilledWorker",
        on_delete=models.CASCADE,
        verbose_name="skilled worker",
    )
    certification_name = models.CharField(max_length=225, null=True)
    description = models.TextField(max_length=2000, null=True)
    date_earned = models.DateField(null=True)
    certification_issued = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.certification_name)
