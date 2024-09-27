from rest_framework import serializers

from notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_for_display = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "notification_for_display", "body", "is_read"]

    def get_notification_for_display(self, obj):
        return obj.get_notification_for_display()
