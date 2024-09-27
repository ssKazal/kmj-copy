import datetime
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel


class ResetPasswordRequestManager(models.Manager):
    """Checks the ResetPasswordRequest object validity time

    Methods
    -------
    active_email():
        Returns ResetPasswordRequest object

    active_sms():
        Returns ResetPasswordRequest object
    """

    def active_email(self):
        """Checks EMAIL_VALIDITY_TIME(24hr) returns ResetPasswordRequest object"""

        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.EMAIL_VALIDITY_TIME
        )
        valid_token = ResetPasswordRequest.objects.filter(created__gte=time_threshold)
        return valid_token

    def active_sms(self):
        """Checks SMS_VALIDITY_TIME(1hr) and returns ResetPasswordRequest object"""

        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.SMS_VALIDITY_TIME
        )
        valid_token = ResetPasswordRequest.objects.filter(created__gte=time_threshold)
        return valid_token


class ResetPasswordRequest(TimeStampedModel):

    _requested_with_choices = (("phone", "Phone"), ("email", "Email"))

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, verbose_name="user")
    requested_with = models.CharField(
        max_length=10, choices=_requested_with_choices, null=True
    )
    token = models.CharField(max_length=10, null=True, blank=True)
    is_used = models.BooleanField(default=False)

    objects = ResetPasswordRequestManager()

    class Meta:
        verbose_name = "Forget Password"
        verbose_name_plural = "Forget Passwords"

    def clean(self, *args, **kwargs):

        # In one-minute can sent one 'request'
        time_threshold = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.TOKEN_REQUEST_TIMEOUT
        )
        request_qs = ResetPasswordRequest.objects.filter(
            user=self.user, created__gte=time_threshold
        )
        if request_qs:
            raise ValidationError("With in one minute can sent one request")
