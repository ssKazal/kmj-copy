import uuid
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


class ChatRoom(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    room_member_1 = models.ForeignKey(User, null=True, related_name='member_1', on_delete=models.SET_NULL)
    room_member_2 = models.ForeignKey(User, null=True, related_name='member_2', on_delete=models.SET_NULL)
    is_blocked_by_member_1 = models.BooleanField(default=False)
    is_blocked_by_member_2 = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def __str__(self):
        return f"{self.room_member_1}-{self.room_member_2}"

    @property
    def group_name(self):
        """Returns private chat room name"""
        return f"PrivateChatRoom-{self.uuid}"

    def clean(self, *args, **kwargs):
        """Unique together between room_member_1 and room_member_2"""

        rooms = ChatRoom.objects.filter(
                    Q(Q(room_member_1=self.room_member_1) & Q(room_member_2=self.room_member_1)) |
                    Q(Q(room_member_2=self.room_member_2) & Q(room_member_2=self.room_member_2)) 
                )

        if self.id: # when update exclude self instance
            rooms = rooms.exclude(id=self.id)

        if rooms.exists():
            raise ValidationError("Rooms with those user already exists") # through error

        return super().clean(*args, **kwargs)

    def get_room_partner(self, user):
        """Returns room partner by taking request user"""
        if user == self.room_member_1:
            return self.room_member_2
        return self.room_member_1


class ChatRoomBlockLog(TimeStampedModel):
    __BLOCK_TYPE = (
        ('blocked', 'Blocked'),
        ('unblocked', 'Unblocked'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    block_type = models.CharField(max_length=20, null=True, choices=__BLOCK_TYPE)
    blocked_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='blocked_by_user')
    blocked_to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='blocked_to_user')

    class Meta:
        verbose_name = "Chat Room Block Log"
        verbose_name_plural = "Chat Room Block Logs"

    def __str__(self):
        return f"{self.blocked_by_user} -> {self.blocked_to_user}"
