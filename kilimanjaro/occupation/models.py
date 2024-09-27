import uuid
from inspect import cleandoc

from celery.utils.functional import uniq
from django.db import models
from model_utils.models import TimeStampedModel


class Occupation(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return str(self.name)

    """
        clean method call is mandatory for this model because of 
        occupation name should be title cased for every object
    """

    def clean(self, *args, **kwargs):
        self.name = (
            self.name.capitalize()
        )  # title cased and case insensitive name saving
