import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Notification(TimeStampedModel):

    _notification_for_choices = (
        ("order_create", "Order Create"),
        ("order_update", "Order Update"),
    )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, verbose_name="user")
    notification_for = models.CharField(
        max_length=100, choices=_notification_for_choices, null=True
    )
    body = models.CharField(max_length=225, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
