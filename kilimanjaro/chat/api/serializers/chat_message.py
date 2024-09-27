from rest_framework import serializers
from chat.models import ChatMessage

from django.conf import settings


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    attachment_links = serializers.SerializerMethodField()
    send_by = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ("id", 'sender', 'message_type', 'send_by',
                'message_text', 'attachment_links', 'is_deleted', 'created_at')

    def get_sender(self, obj):
        sender = obj.sender
        return {
            'id': sender.id,
            'username': sender.__str__(),
            'profile_pic': sender.profile_image
        }

    def get_attachment_links(self, obj):
        # Adds site host to all attachment link
        attachment_links = []
        if obj.attachment_links:
            attachment_links = [f"{settings.SITE_HOST}{link}" for link in obj.attachment_links]
        return attachment_links

    def get_send_by(self, obj):
        return "me" if obj.sender == self.context['request'].user else "other"

    def get_created_at(self, obj):
        return {
            "date": obj.created.strftime("%d %b, %Y"),
            "time": obj.created.strftime("%I:%M %p")
        }

    



