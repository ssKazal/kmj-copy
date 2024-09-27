from rest_framework import serializers
from chat.models import ChatRoom
from chat.models import ChatMessage
from .chat_message import ChatMessageSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    chat_room_partner = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    blocked_by_partner = serializers.SerializerMethodField()
    blocked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ("id", 'chat_room_partner', 'blocked_by_partner', 'blocked_by_me', 'messages')

    def get_chat_room_partner(self, obj):
        partner = obj.get_room_partner(self.context['request'].user)
        return {
            'id': partner.id,
            'username': partner.__str__(),
            'profile_pic': partner.profile_image
        }

    def get_messages(self, obj):
        messages = ChatMessage.objects.filter(room=obj)[:10]
        serializer = ChatMessageSerializer(messages, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_blocked_by_partner(self, obj):
        user = self.context['request'].user
        if user == obj.room_member_1:
            return obj.is_blocked_by_member_2
        elif user == obj.room_member_2:
            return obj.is_blocked_by_member_1

    def get_blocked_by_me(self, obj):
        user = self.context['request'].user
        if user == obj.room_member_1:
            return obj.is_blocked_by_member_1
        elif user == obj.room_member_2:
            return obj.is_blocked_by_member_2

class ChatBlockRoomSerializer(serializers.ModelSerializer):
    chat_room_partner = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ("id", 'chat_room_partner')

    def get_chat_room_partner(self, obj):
        partner = obj.get_room_partner(self.context['request'].user)
        return {
            'id': partner.id,
            'username': partner.__str__(),
            'profile_pic': partner.profile_image
        }



