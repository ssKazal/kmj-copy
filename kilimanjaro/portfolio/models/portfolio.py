import uuid

from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel


class Portfolio(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    skilled_worker = models.OneToOneField(
        "skilled_worker.SkilledWorker",
        on_delete=models.CASCADE,
        verbose_name="skilled worker",
    )
    education = models.CharField(max_length=225, null=True)
    certification = models.ForeignKey(
        "certification.Certification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="certification",
    )
    description = models.TextField(max_length=2000, null=True)

    def __str__(self):
        return str(self.skilled_worker)

    def clean(self):

        # Skilled worker can't add another skilled worker certification
        if (
            self.certification
            and self.certification.skilled_worker != self.skilled_worker
        ):
            raise ValidationError("This Certification obj doesn't belong to this user.")
