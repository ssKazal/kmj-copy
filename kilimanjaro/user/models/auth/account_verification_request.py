import datetime
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel


class AccountVerificationRequestManager(models.Manager):
    """Checks the AccountVerificationRequest object validity time

    Methods
    -------
    active_email():
        Returns AccountVerificationRequest object

    active_sms():
        Returns AccountVerificationRequest object
    """

    def active_email(self):
        """Checks EMAIL_VALIDITY_TIME(24hr) and returns AccountVerificationRequest object"""

        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.EMAIL_VALIDITY_TIME
        )
        valid_token = AccountVerificationRequest.objects.filter(
            created__gte=time_threshold
        )
        return valid_token

    def active_sms(self):
        """Checks SMS_VALIDITY_TIME(1hr) and returns AccountVerificationRequest object"""

        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.SMS_VALIDITY_TIME
        )
        valid_token = AccountVerificationRequest.objects.filter(
            created__gte=time_threshold
        )
        return valid_token


class AccountVerificationRequest(TimeStampedModel):

    _verify_by_choices = (("email", "Email"), ("phone", "Phone"))

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, verbose_name="user")
    verify_by = models.CharField(max_length=10, choices=_verify_by_choices, null=True)
    token = models.CharField(max_length=100, null=True)
    is_used = models.BooleanField(default=False)

    objects = AccountVerificationRequestManager()

    class Meta:
        verbose_name = "Account Verification"
        verbose_name_plural = "Account Verifications"

    def clean(self, *args, **kwargs):

        # In one-minute can sent one 'request'
        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.TOKEN_REQUEST_TIMEOUT
        )

        requested_with_phone = None
        requested_with_email = None

        if self.verify_by == "phone":
            requested_with_phone = AccountVerificationRequest.objects.filter(
                user=self.user, verify_by="phone", created__gte=time_threshold
            )

        if self.verify_by == "email":
            requested_with_email = AccountVerificationRequest.objects.filter(
                user=self.user, verify_by="email", created__gte=time_threshold
            )

        if requested_with_phone or requested_with_email:
            raise ValidationError("With in one minute can sent one request")
