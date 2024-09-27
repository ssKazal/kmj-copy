from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import send_notification
from notification.models import Notification


@receiver(post_save, sender=Notification)
def push_notifications(sender, instance, created, **kwargs):
    if created:

        # Sends notification to web socket layer
        send_notification(
            user_id=instance.user.id,
            first_name=instance.user.first_name,
            last_name=instance.user.last_name,
            notification_for=instance.notification_for,
        )  # Custom function to send notification
