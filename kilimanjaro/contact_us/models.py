import datetime
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel

from core.utils.general_data import MAX_CONTACT_US_ATTACHMENT_SIZE
from core.utils.general_func import generate_uids


class ContactUs(TimeStampedModel):
    def _upload_to_attachment(self, filename):
        """Using filename returns "attachment" field file saving path"""

        uid = generate_uids()  # Custom function to generate unique id
        now_time = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        return f"attachment/id-{uid}/{now_time}/{filename}"

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, verbose_name="user")
    title = models.CharField(max_length=225, null=True)
    message = models.TextField(max_length=2000, null=True)
    attachment = models.FileField(
        upload_to=_upload_to_attachment, max_length=1000, null=True, blank=True
    )  # _upload_to_attachment() has called here
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return str(self.title)

    def clean(self):

        # Can't exceed MAX_CONTACT_US_ATTACHMENT_SIZE
        if self.attachment and self.attachment.size > int(
            MAX_CONTACT_US_ATTACHMENT_SIZE
        ):
            raise ValidationError("File size should not exceed 5MB.")
